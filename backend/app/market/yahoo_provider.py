from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import httpx
from pydantic import ValidationError

from app.market.dto import QuoteDTO
from app.market.exceptions import InstrumentNotFoundError, ProviderUnavailableError
from app.market.provider_base import MarketDataProvider


class YahooFinanceProvider(MarketDataProvider):
    """Yahoo Finance API provider.

    Uses the unofficial v8/finance/chart/ endpoint.
    """

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(timeout=10.0)

    @property
    def name(self) -> str:
        return "yahoo"

    async def _fetch_data(self, symbol: str) -> dict[str, Any]:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            "metrics": "high?low?open?close?volume",
            "interval": "1d",
            "range": "1d",
        }
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            response = await self._client.get(url, params=params, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise InstrumentNotFoundError(symbol) from e
            raise ProviderUnavailableError(self.name, f"HTTP Error {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise ProviderUnavailableError(self.name, f"Request failed: {e}") from e

        data = response.json()
        error = data.get("chart", {}).get("error")
        if error:
            if error.get("code") == "Not Found":
                raise InstrumentNotFoundError(symbol)
            raise ProviderUnavailableError(self.name, f"API Error: {error}")

        return data  # type: ignore

    def _parse_quote(self, symbol: str, data: dict[str, Any]) -> QuoteDTO:
        try:
            result = data["chart"]["result"][0]
            meta = result["meta"]
            indicators = result["indicators"]["quote"][0]

            # For 1d interval, we might have multiple data points if intra-day, but usually 1
            # We just take the last available index
            idx = -1

            price = Decimal(str(meta["regularMarketPrice"]))
            prev_close = Decimal(str(meta["chartPreviousClose"]))

            change_pct = ((price - prev_close) / prev_close) * Decimal("100")

            high = (
                Decimal(str(indicators["high"][idx]))
                if indicators["high"][idx] is not None
                else price
            )
            low = (
                Decimal(str(indicators["low"][idx]))
                if indicators["low"][idx] is not None
                else price
            )
            open_price = (
                Decimal(str(indicators["open"][idx]))
                if indicators["open"][idx] is not None
                else price
            )
            volume = int(indicators["volume"][idx]) if indicators["volume"][idx] is not None else 0

            timestamp = datetime.fromtimestamp(meta["regularMarketTime"], tz=UTC)

            return QuoteDTO(
                symbol=symbol,
                price=price,
                change_pct=round(change_pct, 4),
                volume=volume,
                high=high,
                low=low,
                open=open_price,
                previous_close=prev_close,
                timestamp=timestamp,
                source_name=self.name,
                freshness_seconds=(datetime.now(UTC) - timestamp).total_seconds(),
                is_stale=False,
                data_state="DELAYED",
                is_mock=False,
            )
        except (KeyError, IndexError, TypeError, ValueError, ValidationError) as e:
            raise ProviderUnavailableError(self.name, f"Failed to parse response: {e}") from e

    async def get_quote(self, symbol: str) -> QuoteDTO:
        data = await self._fetch_data(symbol)
        return self._parse_quote(symbol, data)

    async def get_quotes(self, symbols: list[str]) -> list[QuoteDTO]:
        # Yahoo supports batching via v7/finance/quote?symbols=..., but for simplicity
        # we can just run concurrent requests if it's a small batch
        tasks = [self.get_quote(s) for s in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_quotes = []
        for r in results:
            if isinstance(r, QuoteDTO):
                valid_quotes.append(r)
            elif isinstance(r, InstrumentNotFoundError):
                pass
            elif isinstance(r, Exception):
                # If all failed, we might want to raise ProviderUnavailableError,
                # but the spec says "Symbols that fail individually are omitted...
                # unless the entire batch fails"
                pass

        if not valid_quotes and symbols:
            raise ProviderUnavailableError(self.name, "All quotes in batch failed")

        return valid_quotes

    async def get_historical_quotes(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> list[QuoteDTO]:
        period1 = int(start_date.timestamp())
        period2 = int(end_date.timestamp())
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            "period1": str(period1),
            "period2": str(period2),
            "interval": "1d",
            "events": "history",
        }
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

        try:
            response = await self._client.get(url, params=params, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise InstrumentNotFoundError(symbol) from e
            raise ProviderUnavailableError(self.name, f"HTTP Error {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise ProviderUnavailableError(self.name, f"Request failed: {e}") from e

        data = response.json()
        error = data.get("chart", {}).get("error")
        if error:
            if error.get("code") == "Not Found":
                raise InstrumentNotFoundError(symbol)
            raise ProviderUnavailableError(self.name, f"API Error: {error}")

        try:
            result = data["chart"]["result"][0]
            timestamps = result.get("timestamp", [])
            indicators = result["indicators"]["quote"][0]

            quotes = []
            for i, ts in enumerate(timestamps):
                if indicators["open"][i] is None or indicators["close"][i] is None:
                    continue

                price = Decimal(str(indicators["close"][i]))
                open_price = Decimal(str(indicators["open"][i]))
                high = (
                    Decimal(str(indicators["high"][i]))
                    if indicators["high"][i] is not None
                    else price
                )
                low = (
                    Decimal(str(indicators["low"][i]))
                    if indicators["low"][i] is not None
                    else price
                )
                volume = int(indicators["volume"][i]) if indicators["volume"][i] is not None else 0

                # Approximate previous_close for history
                change_pct = (
                    ((price - open_price) / open_price) * Decimal("100")
                    if open_price
                    else Decimal("0")
                )

                dt = datetime.fromtimestamp(ts, tz=UTC)

                quotes.append(
                    QuoteDTO(
                        symbol=symbol,
                        price=price,
                        change_pct=round(change_pct, 4),
                        volume=volume,
                        high=high,
                        low=low,
                        open=open_price,
                        previous_close=open_price,
                        timestamp=dt,
                        source_name=self.name,
                        freshness_seconds=0.0,
                        is_stale=False,
                        data_state="EOD",
                        is_mock=False,
                    )
                )
            return quotes
        except (KeyError, IndexError, TypeError, ValueError, ValidationError) as e:
            raise ProviderUnavailableError(
                self.name, f"Failed to parse history response: {e}"
            ) from e

    async def health_check(self) -> bool:
        try:
            # Just check if we can reach the endpoint for a known symbol
            await self.get_quote("AAPL")
            return True
        except Exception:
            return False

import logging
from datetime import datetime

import httpx

from app.core.config import settings

from .base import MacroDTO, MacroProviderBase

logger = logging.getLogger(__name__)

class EVDSProvider(MacroProviderBase):
    def __init__(self):
        self.base_url = "https://evds2.tcmb.gov.tr/service/evds"
        self.api_key = settings.EVDS_API_KEY

    async def is_available(self) -> bool:
        return bool(self.api_key)

    async def get_macro_series(self, series_codes: list[str]) -> list[MacroDTO]:
        if not await self.is_available():
            logger.info("EVDS_API_KEY not set. EVDS provider unavailable.")
            return []

        results = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                for code in series_codes:
                    # EVDS requires series code and dates or latest
                    url = f"{self.base_url}/series={code}&startDate=01-01-2024&endDate=31-12-2024&type=json&key={self.api_key}"
                    resp = await client.get(url)

                    if resp.status_code == 200:
                        data = resp.json()
                        items = data.get("items", [])
                        if items:
                            latest = items[-1]
                            val_str = latest.get(code.replace(".", "_"))
                            if val_str is not None:
                                results.append(MacroDTO(
                                    series_code=code,
                                    value=float(val_str),
                                    timestamp=datetime.now(), # Or parse from items
                                    description=f"TCMB EVDS {code}"
                                ))
                    else:
                        logger.warning(f"EVDS fetch failed for {code}: HTTP {resp.status_code}")
        except Exception as e:
            logger.error(f"EVDS Provider Error: {str(e)}")

        return results

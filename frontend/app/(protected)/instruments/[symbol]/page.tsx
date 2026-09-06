"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { CandlestickChart } from "@/components/CandlestickChart";
import { AlertCircle, Clock } from "lucide-react";
import React, { useMemo } from "react";

async function fetchInstrument(symbol: string) {
  const res = await fetch(`/api/v1/instruments/${symbol}`);
  if (!res.ok) throw new Error("Failed to fetch instrument");
  return res.json();
}

async function fetchQuote(symbol: string) {
  const res = await fetch(`/api/v1/instruments/${symbol}/quote`);
  if (!res.ok) throw new Error("Failed to fetch quote");
  return res.json();
}

async function fetchHistory(symbol: string) {
  const res = await fetch(`/api/v1/instruments/${symbol}/history`);
  if (!res.ok) throw new Error("Failed to fetch history");
  return res.json();
}

export default function InstrumentDetail() {
  const params = useParams();
  const symbol = decodeURIComponent(params.symbol as string);

  const { data: instrument, isLoading: loadingInst } = useQuery({
    queryKey: ["instrument", symbol],
    queryFn: () => fetchInstrument(symbol),
  });

  const { data: quote, isLoading: loadingQuote } = useQuery({
    queryKey: ["quote", symbol],
    queryFn: () => fetchQuote(symbol),
    refetchInterval: 10000,
  });

  const { data: history, isLoading: loadingHistory } = useQuery({
    queryKey: ["history", symbol],
    queryFn: () => fetchHistory(symbol),
  });

  const chartData = useMemo(() => {
    if (!history) return [];
    
    // Map history to Lightweight Charts format
    const formatted = history.map((h: any) => {
      // time must be a string like 'YYYY-MM-DD' for daily data in lightweight-charts
      const dateStr = new Date(h.timestamp).toISOString().split('T')[0];
      return {
        time: dateStr,
        open: Number(h.open),
        high: Number(h.high),
        low: Number(h.low),
        close: Number(h.close),
        value: h.volume,
      };
    });
    
    // If we have a live quote, append or update the last candle
    if (quote && formatted.length > 0) {
      const today = new Date().toISOString().split('T')[0];
      const lastCandle = formatted[formatted.length - 1];
      
      if (lastCandle.time === today) {
        lastCandle.close = Number(quote.price);
        lastCandle.high = Math.max(lastCandle.high, Number(quote.price));
        lastCandle.low = Math.min(lastCandle.low, Number(quote.price));
      } else {
        formatted.push({
          time: today,
          open: Number(quote.open),
          high: Number(quote.high),
          low: Number(quote.low),
          close: Number(quote.price),
          value: quote.volume,
        });
      }
    }
    
    return formatted;
  }, [history, quote]);

  if (loadingInst) return <div className="p-4">Yükleniyor...</div>;
  if (!instrument) return <div className="p-4 text-red-500">Enstrüman bulunamadı.</div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-gray-900">{instrument.symbol}</h1>
            {quote && (
              <span
                className={`px-2 py-1 text-xs font-semibold rounded-full ${
                  quote.is_stale ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-800"
                }`}
              >
                {quote.is_stale ? "STALE" : "LIVE"}
              </span>
            )}
          </div>
          <p className="text-gray-500 text-lg">{instrument.name} &middot; {instrument.exchange}</p>
        </div>
        
        {loadingQuote ? (
          <div className="text-gray-400">Fiyat yükleniyor...</div>
        ) : quote ? (
          <div className="text-right mt-4 md:mt-0">
            <div className="text-4xl font-bold text-gray-900">
              {Number(quote.price).toFixed(2)}
            </div>
            <div
              className={`text-lg font-medium ${
                Number(quote.change_pct) >= 0 ? "text-green-600" : "text-red-600"
              }`}
            >
              {Number(quote.change_pct) >= 0 ? "+" : ""}
              {Number(quote.change_pct).toFixed(2)}%
            </div>
            <div className="text-sm text-gray-400 mt-1 flex items-center justify-end gap-1">
              <Clock size={14} /> {new Date(quote.timestamp).toLocaleString()}
            </div>
          </div>
        ) : (
          <div className="text-red-500 flex items-center gap-1"><AlertCircle size={16}/> Fiyat alınamadı</div>
        )}
      </div>

      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 min-h-[450px]">
        {loadingHistory ? (
          <div className="flex justify-center items-center h-[400px] text-gray-500">
            Grafik verisi yükleniyor...
          </div>
        ) : chartData.length > 0 ? (
          <CandlestickChart data={chartData} />
        ) : (
          <div className="flex justify-center items-center h-[400px] text-gray-500">
            Grafik verisi bulunamadı.
          </div>
        )}
      </div>
    </div>
  );
}

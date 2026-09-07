"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { CandlestickChart } from "@/components/CandlestickChart";
import { AlertCircle, Clock, ExternalLink, Activity } from "lucide-react";
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

async function fetchTechnical(symbol: string) {
  const res = await fetch(`/api/v1/instruments/${symbol}/technical`);
  if (!res.ok) throw new Error("Failed to fetch technical indicators");
  return res.json();
}

async function fetchContext(symbol: string) {
  const res = await fetch(`/api/v1/instruments/${symbol}/context`);
  if (!res.ok) throw new Error("Failed to fetch context");
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
  
  const { data: technical } = useQuery({
    queryKey: ["technical", symbol],
    queryFn: () => fetchTechnical(symbol),
    retry: false,
  });

  const { data: context } = useQuery({
    queryKey: ["context", symbol],
    queryFn: () => fetchContext(symbol),
    retry: false,
  });

  const chartData = useMemo(() => {
    if (!history) return [];
    
    const formatted = history.map((h: any) => {
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

  const technicalData = useMemo(() => {
     const res: any = { sma: [], ema: [], srLevels: [], patterns: [] };
     if (!technical) return res;
     
     if (technical.indicators) {
         technical.indicators.forEach((ind: any) => {
            const dateStr = new Date(ind.timestamp).toISOString().split('T')[0];
            if (ind.sma_20 !== null && ind.sma_20 !== undefined) res.sma.push({ time: dateStr, value: ind.sma_20 });
            if (ind.ema_20 !== null && ind.ema_20 !== undefined) res.ema.push({ time: dateStr, value: ind.ema_20 });
         });
     }
     
     if (technical.support_resistance) {
         res.srLevels = technical.support_resistance;
     }
     
     if (technical.patterns) {
         res.patterns = technical.patterns.map((p: any) => {
             const dateStr = new Date(p.timestamp).toISOString().split('T')[0];
             let type = "neutral";
             if (p.pattern_name.toLowerCase().includes("bullish") || p.pattern_name.toLowerCase().includes("bottom")) {
                 type = "up";
             } else if (p.pattern_name.toLowerCase().includes("bearish") || p.pattern_name.toLowerCase().includes("top")) {
                 type = "down";
             }
             return {
                 time: dateStr,
                 name: p.pattern_name,
                 type
             };
         });
     }
     
     return res;
  }, [technical]);

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
          <CandlestickChart 
            data={chartData} 
            sma={technicalData.sma} 
            ema={technicalData.ema}
            srLevels={technicalData.srLevels}
            patterns={technicalData.patterns} 
          />
        ) : (
          <div className="flex justify-center items-center h-[400px] text-gray-500">
            Grafik verisi bulunamadı.
          </div>
        )}
      </div>
      
      {/* Context / News Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Activity size={20} /> Haber Akışı
            {context?.availability?.news === false && (
                <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded">UNAVAILABLE</span>
            )}
          </h2>
          {context?.news && context.news.length > 0 ? (
            <ul className="space-y-4">
              {context.news.map((item: any, idx: number) => (
                <li key={idx} className="border-b border-gray-100 pb-3 last:border-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-semibold text-blue-600">{item.provider_name}</span>
                    {item.is_synthetic && <span className="text-[10px] bg-gray-100 text-gray-500 px-1 rounded">MOCK</span>}
                    <span className="text-xs text-gray-400">{new Date(item.published_at).toLocaleDateString()}</span>
                  </div>
                  <h3 className="font-medium text-gray-800 leading-tight">
                    {item.url ? <a href={item.url} target="_blank" rel="noreferrer" className="hover:underline flex items-center gap-1">{item.title} <ExternalLink size={12}/></a> : item.title}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">{item.summary}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 text-sm">Haber bulunamadı.</p>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            KAP Bildirimleri
            {context?.availability?.kap === false && (
                <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded">UNAVAILABLE</span>
            )}
          </h2>
          {context?.disclosures && context.disclosures.length > 0 ? (
            <ul className="space-y-4">
              {context.disclosures.map((item: any, idx: number) => (
                <li key={idx} className="border-b border-gray-100 pb-3 last:border-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs text-gray-400">{new Date(item.published_at).toLocaleDateString()}</span>
                  </div>
                  <h3 className="font-medium text-gray-800 leading-tight">{item.title}</h3>
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">{item.content}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 text-sm">KAP bildirimi bulunamadı.</p>
          )}
          
          {context?.macro && context.macro.length > 0 && (
              <div className="mt-6 pt-4 border-t border-gray-100">
                  <h3 className="font-bold text-gray-800 mb-2">Makro Göstergeler</h3>
                  {context.macro.map((m: any, i: number) => (
                      <div key={i} className="flex justify-between items-center text-sm">
                          <span className="text-gray-600">{m.description}</span>
                          <span className="font-medium">{m.value}</span>
                      </div>
                  ))}
              </div>
          )}
        </div>
      </div>
    </div>
  );
}

"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Activity, AlertCircle, Clock, WifiOff } from "lucide-react";
import { useNetwork } from "@/components/NetworkProvider";

async function fetchInstruments() {
  const res = await fetch("/api/v1/instruments?size=4");
  if (!res.ok) throw new Error("Failed to fetch instruments");
  return res.json();
}

async function fetchQuote(symbol: string) {
  const res = await fetch(`/api/v1/instruments/${symbol}/quote`);
  if (!res.ok) throw new Error("Failed to fetch quote");
  return res.json();
}

function MarketCard({ symbol, name }: { symbol: string; name: string }) {
  const { isOnline } = useNetwork();
  const { data: quote, isLoading, isError } = useQuery({
    queryKey: ["quote", symbol],
    queryFn: () => fetchQuote(symbol),
    refetchInterval: isOnline ? 10000 : false, // pause refresh when offline
  });

  return (
    <Link
      href={`/instruments/${symbol}`}
      className="block p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow relative"
    >
      {!isOnline && quote && (
        <span className="absolute top-2 right-2 bg-yellow-100 text-yellow-800 text-[10px] font-bold px-2 py-1 rounded z-10">OFFLINE</span>
      )}
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-bold text-gray-900">{symbol}</h3>
          <p className="text-sm text-gray-500 truncate max-w-[150px]">{name}</p>
        </div>
        {quote && isOnline && (
          <span
            className={`px-2 py-1 text-xs font-semibold rounded-full ${
              quote.is_stale ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-800"
            }`}
          >
            {quote.is_stale ? "STALE" : "LIVE"}
          </span>
        )}
      </div>

      {isLoading ? (
        <div className="h-10 flex items-center text-gray-400 text-sm">Yükleniyor...</div>
      ) : isError ? (
        <div className="h-10 flex items-center text-red-500 text-sm gap-1">
          <AlertCircle size={14} /> {isOnline ? "Veri alınamadı" : "Çevrimdışı"}
        </div>
      ) : quote ? (
        <div>
          <div className="text-2xl font-semibold text-gray-900">
            {Number(quote.price).toFixed(2)}
          </div>
          <div
            className={`text-sm font-medium ${
              Number(quote.change_pct) >= 0 ? "text-green-600" : "text-red-600"
            }`}
          >
            {Number(quote.change_pct) >= 0 ? "+" : ""}
            {Number(quote.change_pct).toFixed(2)}%
          </div>
          <div className="text-xs text-gray-400 mt-2 flex items-center gap-1">
            <Clock size={12} /> Son: {new Date(quote.timestamp).toLocaleTimeString()}
          </div>
        </div>
      ) : null}
    </Link>
  );
}

export default function Dashboard() {
  const { isOnline } = useNetwork();
  const { data, isLoading } = useQuery({
    queryKey: ["instruments", "dashboard"],
    queryFn: fetchInstruments,
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Activity className="text-blue-600" /> Piyasa Özeti
        </h2>
        <Link href="/markets" className="text-blue-600 hover:underline text-sm font-medium">
          Tüm Piyasalar &rarr;
        </Link>
      </div>

      {!isOnline && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-4 rounded-lg flex gap-3 shadow-sm">
          <WifiOff className="shrink-0" />
          <div>
            <strong>STALE / LAST KNOWN DATA</strong>
            <p className="text-sm">İnternet bağlantınız koptu. Fiyatlar otomatik güncellenmiyor.</p>
          </div>
        </div>
      )}

      {isLoading ? (
        <div>Yükleniyor...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {data?.items?.map((inst: any) => (
            <MarketCard key={inst.symbol} symbol={inst.symbol} name={inst.name} />
          ))}
        </div>
      )}
    </div>
  );
}
"use client";

import { useQuery } from "@tanstack/react-query";
import { TrendingUp, ShieldAlert, WifiOff } from "lucide-react";
import { useNetwork } from "@/components/NetworkProvider";

export default function OpportunitiesPage() {
  const { isOnline } = useNetwork();
  const { data: opportunities, isLoading, dataUpdatedAt } = useQuery({
    queryKey: ["opportunities"],
    queryFn: async () => {
      const res = await fetch("/api/v1/opportunities/scan");
      if (!res.ok) throw new Error("Failed to load");
      return res.json();
    }
  });

  const staleTime = new Date(dataUpdatedAt).toLocaleTimeString();

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-8">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <TrendingUp className="text-indigo-600" /> Fırsat Tarayıcı
          </h1>
          <p className="text-gray-600">Decision Engine ve risk profilinize uygun fırsatlar.</p>
        </div>
      </div>

      {!isOnline && opportunities && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-4 rounded-lg flex gap-3 shadow-sm">
          <WifiOff className="shrink-0" />
          <div>
            <strong>STALE / LAST KNOWN DATA</strong>
            <p className="text-sm">İnternet bağlantınız koptu. Gördüğünüz liste canlı piyasa verisi değildir (Son güncellenme: {staleTime}). Lütfen işlem yapmadan önce bağlantınızı kontrol edin.</p>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="p-6 text-gray-500">Hesaplanıyor...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {opportunities?.map((opp: any) => (
            <div key={opp.symbol} className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 relative">
              {!isOnline && (
                <span className="absolute top-2 right-2 bg-yellow-100 text-yellow-800 text-[10px] font-bold px-2 py-1 rounded">STALE</span>
              )}
              <h3 className="font-bold text-lg mb-1">{opp.symbol}</h3>
              <p className="text-sm text-gray-500 mb-4">{opp.instrument_name}</p>
              
              <div className="flex justify-between items-center mb-2 text-sm">
                <span className="text-gray-600">Ham Skor:</span>
                <span className="font-mono">{opp.raw_score.toFixed(2)}</span>
              </div>
              
              <div className="flex justify-between items-center mb-2 text-sm">
                <span className="text-gray-600">Kullanıcı Uyumu:</span>
                <span className="font-mono">{opp.user_fit_score.toFixed(2)}</span>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center">
                <span className="font-bold text-indigo-600">{opp.canonical_action}</span>
                <span className="text-xs bg-gray-100 px-2 py-1 rounded text-gray-600">{opp.engine_version}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

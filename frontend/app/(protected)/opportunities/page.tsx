"use client";

import { useQuery } from "@tanstack/react-query";
import { TrendingUp, AlertTriangle, Filter } from "lucide-react";
import { useState } from "react";

export default function OpportunitiesPage() {
  const [portfolioId, setPortfolioId] = useState("");
  
  const { data: portfolios } = useQuery({
    queryKey: ["portfolios"],
    queryFn: async () => {
      const res = await fetch("/api/v1/portfolios");
      if (!res.ok) return [];
      return res.json();
    }
  });

  const { data: opportunities, isLoading } = useQuery({
    queryKey: ["opportunities", portfolioId],
    queryFn: async () => {
      const url = portfolioId ? `/api/v1/opportunities/?portfolio_id=${portfolioId}` : "/api/v1/opportunities/";
      const res = await fetch(url);
      if (!res.ok) throw new Error("Failed to load opportunities");
      return res.json();
    }
  });

  return (
    <div className="max-w-6xl mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <TrendingUp className="text-blue-600" /> Fırsat Tarayıcı
          </h1>
          <p className="text-gray-600">
            Piyasa Görünümü (Raw Opportunity) ve Portföy Uyumu (User Fit) ayrımına dayalı deterministik sıralama.
          </p>
        </div>
        
        <div className="flex items-center gap-2 bg-white p-2 rounded-lg border border-gray-200 shadow-sm">
          <Filter size={16} className="text-gray-400" />
          <select 
            className="border-none focus:ring-0 text-sm bg-transparent"
            value={portfolioId}
            onChange={(e) => setPortfolioId(e.target.value)}
          >
            <option value="">Tüm Piyasa (Portföy Filtresi Yok)</option>
            {portfolios?.map((p: any) => (
              <option key={p.id} value={p.id}>{p.name} (Risk Profili)</option>
            ))}
          </select>
        </div>
      </div>

      {isLoading ? (
        <div>Taranıyor...</div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200 text-sm text-gray-500 uppercase">
                <th className="p-4 font-semibold">Sembol</th>
                <th className="p-4 font-semibold">Piyasa Görünümü</th>
                <th className="p-4 font-semibold text-center">Ham Skor</th>
                {portfolioId && <th className="p-4 font-semibold text-center text-blue-600">User Fit Skor</th>}
                {portfolioId && <th className="p-4 font-semibold">Kişisel Aksiyon</th>}
                <th className="p-4 font-semibold">Uyarılar / Etkenler</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {opportunities?.map((opp: any, idx: number) => (
                <tr key={idx} className={`hover:bg-gray-50 ${opp.missing_data ? 'opacity-60' : ''}`}>
                  <td className="p-4">
                    <div className="font-bold text-gray-800">{opp.instrument_symbol}</div>
                    <div className="text-xs text-gray-500">{opp.instrument_name}</div>
                  </td>
                  <td className="p-4 font-semibold">{opp.market_view}</td>
                  <td className="p-4 text-center">
                    <span className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm">{Number(opp.raw_score).toFixed(1)}</span>
                  </td>
                  
                  {portfolioId && (
                    <td className="p-4 text-center">
                      {opp.user_fit_score ? (
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm font-bold">{Number(opp.user_fit_score).toFixed(1)}</span>
                      ) : '-'}
                    </td>
                  )}
                  {portfolioId && (
                    <td className="p-4 font-semibold text-blue-700">{opp.personal_action || '-'}</td>
                  )}
                  
                  <td className="p-4">
                    <div className="flex flex-wrap gap-1">
                      {opp.missing_data && (
                        <span className="bg-yellow-100 text-yellow-800 text-[10px] px-2 py-1 rounded flex items-center gap-1">
                          <AlertTriangle size={10} /> Eksik Veri
                        </span>
                      )}
                      {opp.warnings?.map((w: string, i: number) => (
                        <span key={i} className="bg-red-50 text-red-700 text-[10px] px-2 py-1 rounded border border-red-100">
                          {w}
                        </span>
                      ))}
                      {opp.reasons?.map((r: string, i: number) => (
                        <span key={`r-${i}`} className="bg-gray-100 text-gray-600 text-[10px] px-2 py-1 rounded">
                          {r}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

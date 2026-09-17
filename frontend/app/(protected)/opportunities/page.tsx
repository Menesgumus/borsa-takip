"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";
import { fetchApi } from "@/lib/api";
import { ChevronRight, Target, ShieldAlert, Star } from "lucide-react";
import { OpportunityListResult } from "@/types/opportunity";

export default function OpportunitiesPage() {
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<number | null>(null);

  const { data: portfolios, isLoading: isPortfoliosLoading } = useQuery({
    queryKey: ["portfolios"],
    queryFn: () => fetchApi("/api/v1/portfolios"),
  });

  const { data: instruments, isLoading } = useQuery({
    queryKey: ["opportunities", selectedPortfolioId],
    queryFn: () => {
      const url = selectedPortfolioId 
        ? `/api/v1/opportunities?portfolio_id=${selectedPortfolioId}&limit=10`
        : `/api/v1/opportunities?limit=10`;
      return fetchApi(url);
    },
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-navy-900 tracking-tight">Fırsatlar</h1>
          <p className="text-navy-700 mt-1">Sistem tarafından belirlenen güncel potansiyeller.</p>
        </div>
        
        <div className="flex flex-col gap-1 min-w-[200px]">
          <label className="text-sm font-medium text-navy-700">Portföy Uyumu İçin Seçin</label>
          <select 
            className="w-full bg-surface border border-navy-800/20 rounded-lg px-3 py-2 text-sm text-navy-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            value={selectedPortfolioId || ""}
            onChange={(e) => setSelectedPortfolioId(e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">Genel Piyasa Görünümü</option>
            {!isPortfoliosLoading && Array.isArray(portfolios) && portfolios.map((p: any) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="bg-primary-50 border border-primary-100 rounded-xl p-5 mb-8 flex gap-4">
        <Target className="text-primary-600 shrink-0 mt-0.5" />
        <div className="text-sm text-navy-800">
          <strong className="block text-navy-900 mb-1">Fırsat Puanlaması Hakkında</strong>
          Piyasa Fırsat Puanı (Raw Market Score), teknik ve temel analize dayalı mutlak pazar potansiyelini gösterir. 
          Kişisel Uyum (User Fit), sizin risk toleransınıza ve portföy yoğunluğunuza göre bu fırsatın sizin için ne kadar uygun olduğunu belirtir.
          <em> En yüksek puan her zaman kesin &quot;Al&quot; demek değildir.</em>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          [1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="h-48 bg-slate-100 animate-pulse rounded-xl border border-slate-200"></div>
          ))
        ) : instruments && (instruments as OpportunityListResult[]).length > 0 ? (
          (instruments as OpportunityListResult[]).map((inst) => (
            <Link key={inst.symbol} href={`/instruments/${inst.symbol}`} className="bg-surface rounded-xl p-6 border border-navy-800/10 shadow-sm hover:shadow-md transition-all group relative overflow-hidden">
              {inst.missing_data && (
                 <div className="absolute top-0 left-0 w-full bg-amber-500/10 text-amber-600 text-[10px] font-bold text-center py-1 uppercase tracking-wider">
                   Yetersiz Veri
                 </div>
              )}
              
              <div className={`flex justify-between items-start mb-4 ${inst.missing_data ? "mt-4" : ""}`}>
                <div>
                  <h3 className="text-lg font-bold text-navy-900 group-hover:text-primary-600 transition-colors">{inst.symbol}</h3>
                  <p className="text-sm text-navy-700/60 truncate max-w-[150px]">{inst.name || 'Hisse Senedi'}</p>
                </div>
                <div className="flex gap-1">
                  <span className={`px-2 py-1 text-xs font-bold rounded ${
                    inst.personal_action === "STRONG_BUY" || inst.market_view === "STRONG_BUY" ? "bg-success-100 text-success-800" :
                    inst.personal_action === "BUY" || inst.market_view === "BUY" ? "bg-success-50 text-success-700" :
                    inst.personal_action === "HOLD" || inst.market_view === "HOLD" ? "bg-amber-50 text-amber-700" :
                    "bg-danger-50 text-danger-700"
                  }`}>
                    {inst.personal_action || inst.market_view}
                  </span>
                </div>
              </div>

              <div className="space-y-3 mt-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-navy-700/80">Piyasa Fırsatı</span>
                  <div className="flex items-center gap-1 font-bold text-navy-900">
                    <Star size={14} className="text-amber-400 fill-amber-400" />
                    {Number(inst.market_score || 0).toFixed(0)}
                  </div>
                </div>
                
                {selectedPortfolioId && inst.personal_score !== null && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-navy-700/80">Kişisel Skor</span>
                    <span className="font-bold text-primary-600">
                      {Number(inst.personal_score).toFixed(0)}
                    </span>
                  </div>
                )}
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-navy-700/80">Veri Kalitesi</span>
                  <span className={`text-sm font-medium ${inst.data_quality_score < 50 ? "text-danger-600" : "text-navy-900"}`}>
                    {Number(inst.data_quality_score || 0).toFixed(0)}
                  </span>
                </div>
                
                {selectedPortfolioId && inst.sizing_state === "OK" && inst.recommended_quantity && (
                   <div className="flex justify-between items-center bg-primary-50 p-2 rounded mt-2 border border-primary-100">
                     <span className="text-xs font-medium text-primary-800">Önerilen Sizing</span>
                     <span className="text-xs font-bold text-primary-700">{inst.recommended_quantity} Adet</span>
                   </div>
                )}
              </div>

              <div className="mt-5 pt-4 border-t border-slate-100 text-sm font-medium text-primary-600 flex items-center justify-between">
                Detayları İncele
                <ChevronRight size={16} />
              </div>
            </Link>
          ))
        ) : (
          <div className="col-span-full bg-surface rounded-xl p-12 border border-navy-800/10 shadow-sm text-center">
            <ShieldAlert className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-navy-900 mb-1">Şu An Fırsat Bulunmuyor</h3>
            <p className="text-navy-700">Piyasa koşulları ve veri kalitesi kriterlerini karşılayan yeni fırsatlar burada listelenecektir.</p>
          </div>
        )}
      </div>
    </div>
  );
}

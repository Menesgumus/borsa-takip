"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useState, useEffect } from "react";
import { fetchApi } from "@/lib/api";
import { ChevronRight, Target, ShieldAlert, Star, Wallet, PieChart as PieChartIcon } from "lucide-react";
import { OpportunityListResult } from "@/types/opportunity";
import { formatTry, formatPercent, formatActionLabel, getActionColorClass } from "@/lib/financialUi";
import { DataStateBadge } from "@/components/DataStateBadge";

export default function OpportunitiesPage() {
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<number | null>(null);

  const { data: portfolios, isLoading: isPortfoliosLoading } = useQuery({
    queryKey: ["portfolios"],
    queryFn: () => fetchApi("/api/v1/portfolios"),
  });

  // Auto-select portfolio or load from localStorage
  useEffect(() => {
    if (portfolios && Array.isArray(portfolios)) {
      const saved = localStorage.getItem("last_selected_portfolio");
      if (saved && portfolios.some(p => p.id === Number(saved))) {
        setSelectedPortfolioId(Number(saved));
      } else if (portfolios.length === 1) {
        setSelectedPortfolioId(portfolios[0].id);
      }
    }
  }, [portfolios]);

  const handlePortfolioChange = (id: number | null) => {
    setSelectedPortfolioId(id);
    if (id) {
      localStorage.setItem("last_selected_portfolio", id.toString());
    } else {
      localStorage.removeItem("last_selected_portfolio");
    }
  };

  const { data: instruments, isLoading } = useQuery({
    queryKey: ["opportunities", selectedPortfolioId],
    queryFn: () => {
      const url = selectedPortfolioId 
        ? `/api/v1/opportunities?portfolio_id=${selectedPortfolioId}&limit=20`
        : `/api/v1/opportunities?limit=20`;
      return fetchApi(url);
    },
  });

  const selectedPortfolio = portfolios && Array.isArray(portfolios) ? portfolios.find(p => p.id === selectedPortfolioId) : null;

  // Categorize opportunities
  const opportunities = (instruments as OpportunityListResult[]) || [];
  
  const actionable: OpportunityListResult[] = [];
  const watchlist: OpportunityListResult[] = [];
  const insufficientData: OpportunityListResult[] = [];

  opportunities.forEach(inst => {
    if (inst.missing_data || inst.data_quality_score < 50) {
      insufficientData.push(inst);
    } else {
      const action = inst.personal_action || inst.market_view;
      if ((action === "BUY" || action === "STRONG_BUY") && (!selectedPortfolioId || inst.sizing_state === "OK")) {
        actionable.push(inst);
      } else {
        watchlist.push(inst);
      }
    }
  });

  const renderCard = (inst: OpportunityListResult) => {
    const action = inst.personal_action || inst.market_view;
    const isMissing = inst.missing_data || inst.data_quality_score < 50;
    
    return (
      <Link key={inst.symbol} href={`/opportunities/${inst.symbol}${selectedPortfolioId ? `?portfolio_id=${selectedPortfolioId}` : ''}`} className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm hover:shadow-md transition-all group relative overflow-hidden flex flex-col justify-between">
        {isMissing && (
           <div className="absolute top-0 left-0 w-full bg-amber-500/10 text-amber-600 text-[10px] font-bold text-center py-1 uppercase tracking-wider">
             Yetersiz Veri
           </div>
        )}
        
        <div className={`flex justify-between items-start mb-4 ${isMissing ? "mt-4" : ""}`}>
          <div>
            <h3 className="text-lg font-bold text-navy-900 group-hover:text-primary-600 transition-colors flex items-center gap-2">
              {inst.symbol}
            </h3>
            <p className="text-sm text-navy-700/60 truncate max-w-[150px]">{inst.name || 'Hisse Senedi'}</p>
          </div>
          <div className="flex flex-col items-end gap-1">
            <span className={`px-2 py-1 text-xs font-bold rounded border ${getActionColorClass(action, isMissing)}`}>
              {formatActionLabel(action, isMissing)}
            </span>
            {inst.quote_data_state && <DataStateBadge state={inst.quote_data_state} />}
          </div>
        </div>

        <div className="space-y-2 mt-2 mb-4">
          <div className="flex justify-between items-center text-sm">
            <span className="text-navy-700/80">Fiyat</span>
            <span className="font-medium text-navy-900">{formatTry(inst.quote_price)}</span>
          </div>

          <div className="flex justify-between items-center text-sm">
            <span className="text-navy-700/80">Piyasa Puanı</span>
            <div className="flex items-center gap-1 font-bold text-navy-900">
              <Star size={14} className="text-amber-400 fill-amber-400" />
              {inst.market_score !== null ? Number(inst.market_score).toFixed(0) : "—"}
            </div>
          </div>
          
          {selectedPortfolioId && (
            <div className="flex justify-between items-center text-sm">
              <span className="text-navy-700/80">Kişisel Uyum</span>
              <span className="font-bold text-primary-600">
                {inst.personal_score !== null ? Number(inst.personal_score).toFixed(0) : "—"}
              </span>
            </div>
          )}
          
          <div className="flex justify-between items-center text-sm">
            <span className="text-navy-700/80">Veri Kalitesi</span>
            <span className={`font-medium ${inst.data_quality_score < 50 ? "text-danger-600" : "text-navy-900"}`}>
              {inst.data_quality_score !== null ? Number(inst.data_quality_score).toFixed(0) : "Yetersiz Veri"}
            </span>
          </div>
        </div>
        
        {selectedPortfolioId && (
           <div className={`p-3 rounded-lg border mt-auto ${inst.sizing_state === "OK" ? "bg-primary-50 border-primary-100" : "bg-slate-50 border-slate-200"}`}>
             {inst.sizing_state === "OK" ? (
               <>
                 <div className="flex justify-between items-center mb-1">
                   <span className="text-xs font-medium text-primary-800">Önerilen Alım:</span>
                   <span className="text-sm font-bold text-primary-700">{formatTry(inst.recommended_budget)}</span>
                 </div>
                 <div className="flex justify-between items-center mb-1">
                   <span className="text-xs font-medium text-primary-800">Adet:</span>
                   <span className="text-xs font-bold text-primary-700">{inst.recommended_quantity} Lot</span>
                 </div>
                 {(inst.max_additional_budget != null && inst.max_additional_budget > 0) && (
                   <div className="flex justify-between items-center mb-1">
                     <span className="text-xs font-medium text-primary-800">Azami ek alım:</span>
                     <span className="text-xs font-medium text-primary-700">
                       {formatTry(inst.max_additional_budget)} / {inst.max_additional_quantity} adet
                     </span>
                   </div>
                 )}
                 <div className="flex justify-between items-center">
                   <span className="text-xs font-medium text-primary-800">İşlem Sonrası Pay:</span>
                   <span className="text-xs font-bold text-primary-700">{formatPercent(inst.estimated_post_trade_weight)}</span>
                 </div>
               </>
             ) : (
               <div className="text-xs font-medium text-slate-600">
                 {inst.sizing_state === "OVER_LIMIT" ? "Portföy yoğunluk sınırı nedeniyle yeni alım uygun değil." :
                  inst.sizing_state === "NO_CASH" ? "Bu portföyde en az 1 adet alım için yeterli nakit yok." :
                  inst.sizing_state === "NOT_ACTIONABLE" ? "Mevcut karar ve risk koşullarında ek alım önerilmiyor." :
                  inst.sizing_state === "VALUATION_INCOMPLETE" ? "Portföyünüzdeki bazı varlıkların fiyatı alınamadığı için güvenilir alım miktarı hesaplanamıyor." :
                  "Alım için uygun değil."}
               </div>
             )}
           </div>
        )}

        <div className="mt-4 pt-3 border-t border-slate-100 text-sm font-medium text-primary-600 flex items-center justify-between">
          Detayları İncele
          <ChevronRight size={16} />
        </div>
      </Link>
    );
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-navy-900 tracking-tight">Fırsatlar</h1>
          <p className="text-navy-700 mt-1">Sistem tarafından belirlenen güncel potansiyeller.</p>
        </div>
        
        <div className="flex flex-col gap-1 min-w-[250px]">
          <label className="text-sm font-medium text-navy-700">Portföy Uyumu İçin Seçin</label>
          <select 
            className="w-full bg-surface border border-navy-800/20 rounded-lg px-3 py-2 text-sm text-navy-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            value={selectedPortfolioId || ""}
            onChange={(e) => handlePortfolioChange(e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">Genel Piyasa Görünümü</option>
            {!isPortfoliosLoading && Array.isArray(portfolios) && portfolios.map((p: any) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>
      </div>

      {selectedPortfolio && (
        <div className="bg-white border border-slate-200 rounded-xl p-4 flex flex-wrap gap-6 items-center shadow-sm">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary-50 rounded-lg text-primary-600">
              <PieChartIcon size={20} />
            </div>
            <div>
              <div className="text-xs text-slate-500 font-medium">Seçili Portföy</div>
              <div className="font-bold text-navy-900">{selectedPortfolio.name}</div>
            </div>
          </div>
          <div className="w-px h-8 bg-slate-200 hidden sm:block"></div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-50 rounded-lg text-emerald-600">
              <Wallet size={20} />
            </div>
            <div>
              <div className="text-xs text-slate-500 font-medium">Kullanılabilir Nakit</div>
              <div className="font-bold text-navy-900">{formatTry(selectedPortfolio.cash_balance)}</div>
            </div>
          </div>
          <div className="w-px h-8 bg-slate-200 hidden sm:block"></div>
          <div>
            <div className="text-xs text-slate-500 font-medium">Toplam Değer</div>
            <div className="font-bold text-navy-900">
              {selectedPortfolio.total_market_value != null 
                ? formatTry(Number(selectedPortfolio.total_market_value)) 
                : "Kısmi Veri"}
            </div>
          </div>
        </div>
      )}

      {!isLoading && (
        <div className="flex gap-4 border-b border-slate-200 pb-2">
          <div className="text-sm font-bold text-navy-900">Alım Fırsatı: <span className="text-success-600">{actionable.length}</span></div>
          <div className="text-sm font-bold text-navy-900">İzle: <span className="text-amber-600">{watchlist.length}</span></div>
          <div className="text-sm font-bold text-navy-900">Yetersiz Veri: <span className="text-slate-500">{insufficientData.length}</span></div>
        </div>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="h-64 bg-slate-100 animate-pulse rounded-xl border border-slate-200"></div>
          ))}
        </div>
      ) : (
        <div className="space-y-10">
          {actionable.length > 0 && (
            <section>
              <h2 className="text-xl font-bold text-navy-900 mb-4 flex items-center gap-2">
                <Target className="text-primary-600" size={24} /> 
                Alım Fırsatları
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {actionable.map(renderCard)}
              </div>
            </section>
          )}

          {watchlist.length > 0 && (
            <section>
              <h2 className="text-xl font-bold text-navy-900 mb-4 flex items-center gap-2">
                <ShieldAlert className="text-amber-600" size={24} /> 
                İzlemeye Değer
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 opacity-90">
                {watchlist.map(renderCard)}
              </div>
            </section>
          )}

          {insufficientData.length > 0 && (
            <section>
              <h2 className="text-lg font-bold text-slate-500 mb-4">Verisi Yetersiz</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 opacity-60">
                {insufficientData.map(renderCard)}
              </div>
            </section>
          )}

          {opportunities.length === 0 && (
            <div className="bg-surface rounded-xl p-12 border border-navy-800/10 shadow-sm text-center">
              <ShieldAlert className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <h3 className="text-lg font-bold text-navy-900 mb-1">Şu An Fırsat Bulunmuyor</h3>
              <p className="text-navy-700">Piyasa koşulları ve veri kalitesi kriterlerini karşılayan yeni fırsatlar burada listelenecektir.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

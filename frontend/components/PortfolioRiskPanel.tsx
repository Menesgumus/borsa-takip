"use client";
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertCircle, ShieldAlert, PieChart } from "lucide-react";
import { fetchApi } from "@/lib/api";
import { formatTry, formatPercent } from "@/lib/financialUi";
import { DataStateBadge } from "@/components/DataStateBadge";

export function PortfolioRiskPanel({ portfolioId }: { portfolioId: string }) {
  const { data: risk, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["portfolio-risk", portfolioId],
    queryFn: () => fetchApi(`/api/v1/portfolios/${portfolioId}/risk`),
  });

  if (isLoading) return <div className="p-6 text-slate-500">Risk profili hesaplanıyor...</div>;

  if (isError) {
    return (
      <div className="space-y-6 max-w-5xl mx-auto py-6">
        <div className="bg-red-50 text-red-600 rounded-xl p-6 border border-red-200 flex flex-col items-center gap-4">
          <AlertCircle size={32} />
          <div className="font-medium text-lg">
            {(error as any)?.name === 'RequestTimeoutError' ? 'Risk verileri zamanında alınamadı.' :
             (error as any)?.name === 'NetworkError' ? 'Servise şu anda ulaşılamıyor.' :
             'Risk profili hesaplanırken sunucu hatası oluştu.'}
          </div>
          <button onClick={() => refetch()} className="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors">
            Tekrar Dene
          </button>
        </div>
      </div>
    );
  }

  // Honest empty state
  if (!risk || (risk as any).coverage_percentage === 0 || (risk as any).total_market_value === 0) {
    return (
      <div className="space-y-6 max-w-5xl mx-auto py-6">
        <div className="bg-slate-50 text-slate-600 rounded-xl p-8 border border-slate-200 flex flex-col items-center gap-3 text-center">
          <PieChart size={40} className="text-slate-400" />
          <h2 className="text-lg font-semibold text-slate-700">Yetersiz Veri (INSUFFICIENT_DATA)</h2>
          <p className="max-w-md">Portföyünüzde risk analizi yapmak için yeterli varlık veya güncel fiyat verisi bulunmuyor.</p>
        </div>
      </div>
    );
  }

  const r = risk as any;

  return (
    <div className="space-y-6 max-w-5xl mx-auto py-6 animate-in fade-in duration-500">
      <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
        <h1 className="text-2xl font-bold flex items-center gap-2 mb-3 text-navy-900">
          <ShieldAlert className="text-red-500" />
          Portföy Risk ve Konsantrasyon Analizi
        </h1>
        <div className="flex flex-wrap items-center gap-3 text-sm text-slate-600">
          <span className="font-medium">Kapsanan Değer: {formatPercent(r.coverage_percentage)}</span>
          <span className="w-1.5 h-1.5 rounded-full bg-slate-300"></span>
          <span>Analiz Edilen Varlık: {r.analyzed_positions_count} / {r.total_positions_count}</span>
          <span className="w-1.5 h-1.5 rounded-full bg-slate-300"></span>
          <DataStateBadge state={r.data_freshness_state} />
        </div>
        
        {r.coverage_percentage < 1 && (
          <div className="mt-4 p-3 bg-yellow-50 text-yellow-800 border border-yellow-200 rounded-md text-sm flex gap-2">
            <AlertCircle size={18} className="shrink-0" />
            <p><strong>Dikkat:</strong> Bazı varlıkların anlık fiyatı bulunamadığı için risk analizi portföyün sadece %{formatPercent(r.coverage_percentage * 100)}&apos;lik kısmını kapsamaktadır. Gecikmeli veya EOD veri kullanılıyor olabilir.</p>
          </div>
        )}
      </div>

      {r.warnings?.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-5 space-y-3">
          <h2 className="font-semibold text-red-800 flex items-center gap-2">
            <AlertCircle size={18} /> Konsantrasyon İhlalleri
          </h2>
          <ul className="space-y-3">
            {r.warnings.map((w: any, idx: number) => (
              <li key={idx} className="flex flex-col gap-1 bg-white/60 p-3 rounded-md border border-red-100">
                <div className="font-medium text-red-900">
                  <span className="font-bold">{w.symbol}</span> ağırlığı çok yüksek!
                </div>
                <div className="text-sm text-red-700 flex flex-wrap gap-x-4 gap-y-1">
                  <span>Mevcut: <strong>{formatPercent(w.actual_weight)}</strong></span>
                  <span>Limit: <strong>{formatPercent(w.limit_weight)}</strong></span>
                  <span>Önerilen Azaltım: <strong className="line-through">{formatTry(w.suggested_reduction_value)}</strong> (Hata)</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {r.concentrations?.map((c: any) => (
          <div key={c.symbol} className="bg-white p-4 rounded-lg shadow-sm border border-slate-200 flex flex-col gap-2">
            <div className="flex justify-between items-center">
              <span className="font-bold text-navy-900 text-lg">{c.symbol}</span>
              <span className={`px-2 py-0.5 text-xs font-semibold rounded-md ${
                c.is_compliant 
                  ? 'bg-green-100 text-green-700'
                  : 'bg-red-100 text-red-700'
              }`}>
                {c.is_compliant ? 'Uygun' : 'Limit Aşımı'}
              </span>
            </div>
            
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Mevcut Ağırlık:</span>
                <span className={`font-semibold ${c.is_compliant ? 'text-slate-700' : 'text-red-600'}`}>
                  {formatPercent(c.actual_weight)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Risk Limiti:</span>
                <span className="font-medium text-slate-700">{formatPercent(c.limit_weight)}</span>
              </div>
              
              {!c.is_compliant && c.excess_value > 0 && (
                <div className="mt-2 pt-2 border-t border-slate-100">
                  <div className="flex justify-between text-sm">
                    <span className="text-red-500">Aşım Tutarı:</span>
                    <span className="font-semibold text-red-600">{formatTry(c.excess_value)}</span>
                  </div>
                </div>
              )}
            </div>
            
            <div className="w-full bg-slate-100 rounded-full h-2 mt-2">
              <div 
                className={`h-2 rounded-full ${c.is_compliant ? 'bg-primary-500' : 'bg-red-500'}`}
                style={{ width: `${Math.min(c.actual_weight * 100, 100)}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

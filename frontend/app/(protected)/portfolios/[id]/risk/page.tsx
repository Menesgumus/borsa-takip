"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertCircle, ShieldAlert, PieChart } from "lucide-react";
import { useParams } from "next/navigation";
import { fetchApi } from "@/lib/api";
import { formatTry, formatPercent } from "@/lib/financialUi";
import { DataStateBadge } from "@/components/DataStateBadge";

export default function PortfolioRiskPage() {
  const params = useParams();
  const portfolioId = params.id as string;

  const { data: risk, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["portfolio-risk", portfolioId],
    queryFn: () => fetchApi(`/api/v1/portfolios/${portfolioId}/risk`),
  });

  if (isLoading) return <div className="p-6 text-slate-500">Risk profili hesaplanıyor...</div>;

  if (isError) {
    return (
      <div className="space-y-6 max-w-5xl mx-auto p-6">
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
      <div className="space-y-6 max-w-5xl mx-auto p-6">
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
    <div className="space-y-6 max-w-5xl mx-auto p-6 animate-in fade-in duration-500">
      <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
        <h1 className="text-2xl font-bold flex items-center gap-2 mb-3 text-navy-900">
          <ShieldAlert className="text-red-500" />
          Portföy Risk ve Konsantrasyon Analizi
        </h1>
        <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600">
          <div className="flex items-center gap-2">
            <span className="font-medium">Veri Durumu:</span>
            <DataStateBadge state={r.data_freshness} />
          </div>
          <div className="flex items-center gap-2">
            <span className="font-medium">Kapsam (Coverage):</span>
            <span className="font-bold text-navy-900">{formatPercent(r.coverage_percentage)}</span>
          </div>
        </div>
      </div>

      {r.limit_violations?.length > 0 && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg shadow-sm">
          <h3 className="text-red-800 font-bold flex items-center gap-2 mb-3">
            <AlertCircle size={20} /> Kritik Limit İhlalleri
          </h3>
          <ul className="space-y-2">
            {r.limit_violations.map((v: any, i: number) => (
              <li key={i} className="text-red-700 text-sm flex flex-col sm:flex-row sm:justify-between sm:items-center bg-red-100 p-3 rounded-md gap-2">
                <span className="font-medium">{v.rule_name} ({v.reason_code})</span>
                <span className="font-mono bg-red-50 px-2 py-1 rounded">
                  Limit: <span className="font-bold">{formatPercent(v.limit_value)}</span>, Mevcut: <span className="font-bold">{formatPercent(v.actual_value)}</span>
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 flex flex-col justify-between">
          <h3 className="text-slate-500 font-medium mb-1 text-sm uppercase tracking-wider">Historical VaR (95%, 1-Day)</h3>
          <p className="text-2xl lg:text-3xl font-bold text-navy-900 mt-2">
            {r.historical_var_95_1d != null ? formatTry(r.historical_var_95_1d) : 'Yetersiz Veri'}
          </p>
          <p className="text-xs text-slate-400 mt-2">Geçmiş verilere dayalı tahmin</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 flex flex-col justify-between">
          <h3 className="text-slate-500 font-medium mb-1 text-sm uppercase tracking-wider">Nakit Ağırlığı</h3>
          <p className="text-2xl lg:text-3xl font-bold text-navy-900 mt-2">{formatPercent(r.cash_weight_percentage)}</p>
          <p className="text-xs text-slate-500 mt-2 font-medium">Toplam: {formatTry(r.cash_exposure)}</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 flex flex-col justify-between">
          <h3 className="text-slate-500 font-medium mb-1 text-sm uppercase tracking-wider">Yatırım Ağırlığı</h3>
          <p className="text-2xl lg:text-3xl font-bold text-navy-900 mt-2">{formatPercent(r.invested_weight_percentage)}</p>
          <p className="text-xs text-slate-500 mt-2 font-medium">Toplam: {formatTry(r.invested_exposure)}</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
        <h3 className="text-lg font-bold mb-5 flex items-center gap-2 text-navy-900">
          Varlık Konsantrasyonu
        </h3>
        {(!r.positions_exposure || r.positions_exposure.length === 0) ? (
          <div className="text-center py-6 text-slate-500 text-sm">
            Konsantrasyon hesaplanacak açık pozisyon bulunamadı.
          </div>
        ) : (
          <div className="space-y-5">
            {r.positions_exposure.map((pos: any) => {
              const widthVal = Math.min(100, Math.max(0, Number(pos.weight_percentage) || 0));
              return (
                <div key={pos.instrument_id} className="relative">
                  <div className="flex justify-between items-end mb-1.5 text-sm font-medium">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-navy-900 text-base">{pos.symbol}</span>
                      {pos.is_stale && (
                        <span className="text-[10px] uppercase font-bold text-danger-600 bg-danger-50 px-1.5 py-0.5 rounded border border-danger-100">
                          Eksik Veri
                        </span>
                      )}
                    </div>
                    <span className="font-bold text-slate-700">{formatPercent(pos.weight_percentage)}</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden border border-slate-200">
                    <div 
                      className={`h-full rounded-full transition-all duration-500 ${widthVal > 30 ? 'bg-danger-500' : 'bg-primary-500'}`} 
                      style={{ width: `${widthVal}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

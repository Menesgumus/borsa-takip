"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertCircle, ShieldAlert, PieChart } from "lucide-react";
import { useParams } from "next/navigation";
import { fetchApi } from "@/lib/api";

export default function PortfolioRiskPage() {
  const params = useParams();
  const portfolioId = params.id as string;

  const { data: risk, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["portfolio-risk", portfolioId],
    queryFn: () => fetchApi(`/api/v1/portfolios/${portfolioId}/risk`),
  });

  if (isLoading) return <div className="p-6">Risk profili hesaplanıyor...</div>;

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
  if (!risk || (risk as any).coverage_percentage === 0 || (risk as any).total_value === 0) {
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
    <div className="space-y-6 max-w-5xl mx-auto p-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h1 className="text-2xl font-bold flex items-center gap-2 mb-2">
          <ShieldAlert className="text-red-500" />
          Portföy Risk ve Konsantrasyon Analizi
        </h1>
        <div className="flex gap-4 text-sm text-gray-500">
          <span className={`px-2 py-1 rounded-full font-medium ${r.data_freshness === 'LIVE' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
            Data: {r.data_freshness}
          </span>
          <span>Coverage: {r.coverage_percentage}%</span>
        </div>
      </div>

      {r.limit_violations?.length > 0 && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
          <h3 className="text-red-800 font-bold flex items-center gap-2 mb-2">
            <AlertCircle size={20} /> Kritik Limit İhlalleri
          </h3>
          <ul className="space-y-2">
            {r.limit_violations.map((v: any, i: number) => (
              <li key={i} className="text-red-700 text-sm flex justify-between bg-red-100 p-2 rounded">
                <span>{v.rule_name} ({v.reason_code})</span>
                <span className="font-mono">Limit: {v.limit_value}%, Mevcut: {v.actual_value}%</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-gray-500 font-medium mb-1">Historical VaR (95%, 1-Day)</h3>
          <p className="text-3xl font-bold text-gray-900">
            {r.historical_var_95_1d !== null ? `${r.historical_var_95_1d} TRY` : 'Yetersiz Veri'}
          </p>
          <p className="text-xs text-gray-400 mt-2">Geçmiş verilere dayalı tahmin</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-gray-500 font-medium mb-1">Nakit Ağırlığı</h3>
          <p className="text-3xl font-bold text-gray-900">{r.cash_weight_percentage}%</p>
          <p className="text-xs text-gray-400 mt-2">Toplam: {r.cash_exposure} TRY</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-gray-500 font-medium mb-1">Yatırım Ağırlığı</h3>
          <p className="text-3xl font-bold text-gray-900">{r.invested_weight_percentage}%</p>
          <p className="text-xs text-gray-400 mt-2">Toplam: {r.invested_exposure} TRY</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <PieChart className="text-blue-500" /> Pozisyon Konsantrasyonu
        </h3>
        <div className="space-y-4">
          {r.positions_exposure?.map((pos: any) => (
            <div key={pos.instrument_id} className="relative">
              <div className="flex justify-between mb-1 text-sm font-medium">
                <span>{pos.symbol} {pos.is_stale && <span className="text-xs text-red-500">(Stale)</span>}</span>
                <span>{pos.weight_percentage}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  className={`h-2.5 rounded-full ${pos.weight_percentage > 30 ? 'bg-red-500' : 'bg-blue-500'}`} 
                  style={{ width: `${pos.weight_percentage}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

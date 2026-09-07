"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertCircle, ShieldAlert, PieChart } from "lucide-react";
import { useParams } from "next/navigation";

export default function PortfolioRiskPage() {
  const params = useParams();
  const portfolioId = params.id as string;

  const { data: risk, isLoading } = useQuery({
    queryKey: ["portfolio-risk", portfolioId],
    queryFn: async () => {
      const res = await fetch(`/api/v1/portfolios/${portfolioId}/risk`);
      if (!res.ok) throw new Error("Failed to fetch risk metrics");
      return res.json();
    },
  });

  if (isLoading) return <div className="p-6">Risk profili hesaplanıyor...</div>;

  return (
    <div className="space-y-6 max-w-5xl mx-auto p-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h1 className="text-2xl font-bold flex items-center gap-2 mb-2">
          <ShieldAlert className="text-red-500" />
          Portföy Risk ve Konsantrasyon Analizi
        </h1>
        <div className="flex gap-4 text-sm text-gray-500">
          <span className={`px-2 py-1 rounded-full font-medium ${risk?.data_freshness === 'LIVE' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
            Data: {risk?.data_freshness}
          </span>
          <span>Coverage: {risk?.coverage_percentage}%</span>
        </div>
      </div>

      {risk?.limit_violations?.length > 0 && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
          <h3 className="text-red-800 font-bold flex items-center gap-2 mb-2">
            <AlertCircle size={20} /> Kritik Limit İhlalleri
          </h3>
          <ul className="space-y-2">
            {risk.limit_violations.map((v: any, i: number) => (
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
            {risk?.historical_var_95_1d !== null ? `${risk?.historical_var_95_1d} TRY` : 'Yetersiz Veri'}
          </p>
          <p className="text-xs text-gray-400 mt-2">Geçmiş verilere dayalı tahmin</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-gray-500 font-medium mb-1">Nakit Ağırlığı</h3>
          <p className="text-3xl font-bold text-gray-900">{risk?.cash_weight_percentage}%</p>
          <p className="text-xs text-gray-400 mt-2">Toplam: {risk?.cash_exposure} TRY</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-gray-500 font-medium mb-1">Yatırım Ağırlığı</h3>
          <p className="text-3xl font-bold text-gray-900">{risk?.invested_weight_percentage}%</p>
          <p className="text-xs text-gray-400 mt-2">Toplam: {risk?.invested_exposure} TRY</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <PieChart className="text-blue-500" /> Pozisyon Konsantrasyonu
        </h3>
        <div className="space-y-4">
          {risk?.positions_exposure?.map((pos: any) => (
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

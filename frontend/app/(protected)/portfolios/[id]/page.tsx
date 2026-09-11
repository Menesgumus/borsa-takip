"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { fetchApi } from "@/lib/api";
import { ArrowLeft, AlertCircle, DollarSign, Plus } from "lucide-react";
import { useState } from "react";
import { PortfolioActionModal } from "@/components/PortfolioActionModal";
import { PortfolioCharts } from "@/components/PortfolioCharts";
import { formatTry, formatQuantity, getProfitLossColorClass } from "@/lib/financialUi";
import { DataStateBadge } from "@/components/DataStateBadge";

export default function PortfolioDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const router = useRouter();
  const [isActionModalOpen, setIsActionModalOpen] = useState(false);

  const { data: summary, isLoading, isError, error } = useQuery<any>({
    queryKey: ["portfolio", id, "summary"],
    queryFn: () => fetchApi(`/api/v1/portfolios/${id}/summary`),
    retry: 1,
  });

  const { data: portfolios } = useQuery<any[]>({
    queryKey: ["portfolios"],
    queryFn: () => fetchApi("/api/v1/portfolios"),
  });
  
  const portfolio = portfolios?.find((p: any) => String(p.id) === id);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px] text-slate-500">
        Portföy yükleniyor...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="text-center py-12 flex flex-col items-center gap-4">
        <AlertCircle className="text-danger-500" size={32} />
        <div className="text-danger-700 font-medium">
          Portföy verileri alınamadı.
        </div>
        <div className="text-sm text-slate-500">
          {(error as any)?.message || "Lütfen daha sonra tekrar deneyin."}
        </div>
      </div>
    );
  }

  if (!summary) return null;

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-6xl mx-auto pb-12">
      <div className="flex flex-col md:flex-row md:items-center gap-4 mb-2">
        <button onClick={() => router.push('/portfolios')} className="hidden md:flex text-slate-400 hover:text-navy-900 transition-colors">
          <ArrowLeft size={20} />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-navy-900 flex items-center gap-3">
            <button onClick={() => router.push('/portfolios')} className="md:hidden text-slate-400 hover:text-navy-900 transition-colors">
              <ArrowLeft size={20} />
            </button>
            {portfolio?.name || `Portföy #${id}`}
          </h1>
          <div className="flex flex-wrap items-center gap-2 mt-1 text-sm">
             <span className="px-2 py-0.5 bg-slate-100 text-slate-600 font-semibold rounded">
              {portfolio?.portfolio_type === 'REAL' ? 'GERÇEK' : portfolio?.portfolio_type === 'PAPER' ? 'SİMÜLASYON' : portfolio?.portfolio_type || 'Bilinmiyor'}
            </span>
            <span className="text-slate-500">| Nakit: <span className="font-medium text-navy-900">{formatTry(summary.cash_balance)}</span></span>
          </div>
        </div>
        <div className="md:ml-auto flex items-center gap-3 mt-4 md:mt-0 w-full md:w-auto">
          <button onClick={() => setIsActionModalOpen(true)} className="flex-1 md:flex-none bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm flex items-center justify-center gap-2">
            <Plus size={16} /> Yeni İşlem
          </button>
          <Link href={`/portfolios/${id}/risk`} className="flex-1 md:flex-none text-center bg-navy-900 hover:bg-navy-800 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm">
            Risk Analizi
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm flex flex-col justify-between">
          <div className="text-sm text-navy-700/70 font-medium mb-1">
             Toplam Değer
          </div>
          <div className="text-2xl font-bold text-navy-900">
            {summary.total_market_value != null ? formatTry(summary.total_market_value) : 'Yetersiz Veri'}
          </div>
        </div>
        <div className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm flex flex-col justify-between">
          <div className="text-sm text-navy-700/70 font-medium mb-1">
             Gerçekleşen K/Z
          </div>
          <div className={`text-2xl font-bold ${getProfitLossColorClass(summary.total_realized_pnl)}`}>
            {Number(summary.total_realized_pnl) > 0 ? '+' : ''}{formatTry(summary.total_realized_pnl)}
          </div>
        </div>
        <div className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm flex flex-col justify-between">
          <div className="text-sm text-navy-700/70 font-medium mb-1">
             Gerçekleşmeyen K/Z
          </div>
          <div className={`text-2xl font-bold ${summary.total_unrealized_pnl != null ? getProfitLossColorClass(summary.total_unrealized_pnl) : 'text-slate-700'}`}>
             {summary.total_unrealized_pnl != null ? `${Number(summary.total_unrealized_pnl) > 0 ? '+' : ''}${formatTry(summary.total_unrealized_pnl)}` : 'Yetersiz Veri'}
          </div>
        </div>
        <div className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm flex flex-col justify-between">
          <div className="text-sm text-navy-700/70 font-medium mb-1">
             Yatırılan / Çekilen
          </div>
          <div className="text-lg font-bold text-slate-700">
             +{formatTry(summary.total_deposits)} / -{formatTry(summary.total_withdrawals)}
          </div>
        </div>
      </div>

      <div className="bg-surface rounded-xl border border-navy-800/10 shadow-sm overflow-hidden mt-6">
        <div className="p-5 border-b border-navy-800/10 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
          <h2 className="text-lg font-bold text-navy-900">Açık Pozisyonlar</h2>
          <div className="flex items-center gap-2 text-xs font-medium">
            <span className="text-slate-500">Veri Durumu:</span>
            <DataStateBadge state={summary.market_data_freshness} />
          </div>
        </div>
        
        {summary.positions.length === 0 ? (
          <div className="p-12 text-center text-slate-500 flex flex-col items-center">
            <DollarSign className="w-12 h-12 text-slate-300 mb-3" />
            <p className="font-medium text-navy-900 mb-1">Henüz Pozisyon Yok</p>
            <p className="text-sm">Bu portföyde henüz açık bir pozisyon bulunmuyor.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm min-w-[700px]">
              <thead className="bg-slate-50 text-slate-600 font-medium">
                <tr>
                  <th className="px-5 py-3">Sembol</th>
                  <th className="px-5 py-3 text-right">Adet</th>
                  <th className="px-5 py-3 text-right">Ort. Maliyet</th>
                  <th className="px-5 py-3 text-right">Anlık Fiyat</th>
                  <th className="px-5 py-3 text-right">Piyasa Değeri</th>
                  <th className="px-5 py-3 text-right">Durum (K/Z)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {summary.positions.map((pos: any) => (
                  <tr key={pos.instrument_id} className="hover:bg-slate-50/50">
                    <td className="px-5 py-4 font-semibold text-navy-900">{pos.symbol}</td>
                    <td className="px-5 py-4 text-right font-medium">{formatQuantity(pos.quantity)}</td>
                    <td className="px-5 py-4 text-right text-slate-600">{formatTry(pos.average_cost)}</td>
                    <td className="px-5 py-4 text-right font-medium">
                      {pos.current_price != null ? formatTry(pos.current_price) : 'Yetersiz Veri'}
                    </td>
                    <td className="px-5 py-4 text-right font-medium">
                      {pos.market_value != null ? formatTry(pos.market_value) : 'Yetersiz Veri'}
                    </td>
                    <td className="px-5 py-4 text-right">
                      {pos.unrealized_pnl != null ? (
                        <span className={`font-semibold ${getProfitLossColorClass(pos.unrealized_pnl)}`}>
                          {Number(pos.unrealized_pnl) > 0 ? '+' : ''}{formatTry(pos.unrealized_pnl)}
                        </span>
                      ) : (
                        <span className="text-slate-500 font-medium">Yetersiz Veri</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <PortfolioCharts portfolioId={id} summary={summary} />

      <PortfolioActionModal 
        portfolioId={id} 
        isOpen={isActionModalOpen} 
        onClose={() => setIsActionModalOpen(false)} 
        summary={summary} 
      />
    </div>
  );
}

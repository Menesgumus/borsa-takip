"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { fetchApi } from "@/lib/api";
import { ArrowLeft, AlertCircle, DollarSign } from "lucide-react";

export default function PortfolioDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const router = useRouter();

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
      <div className="flex flex-col items-center justify-center py-20 text-slate-500 gap-3">
        <div className="w-6 h-6 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
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
    <div className="space-y-6 animate-in fade-in duration-500 max-w-6xl mx-auto">
      <div className="flex items-center gap-4 mb-2">
        <button onClick={() => router.push('/portfolios')} className="text-slate-400 hover:text-navy-900 transition-colors">
          <ArrowLeft size={20} />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-navy-900">{portfolio?.name || `Portföy #${id}`}</h1>
          <div className="flex items-center gap-2 mt-1 text-sm">
             <span className="px-2 py-0.5 bg-slate-100 text-slate-600 font-semibold rounded">
              {portfolio?.portfolio_type === 'REAL' ? 'GERÇEK' : portfolio?.portfolio_type === 'PAPER' ? 'SİMÜLASYON' : portfolio?.portfolio_type || 'Bilinmiyor'}
            </span>
            <span className="text-slate-500">• Nakit: {Number(summary.cash_balance).toLocaleString('tr-TR')} ₺</span>
          </div>
        </div>
        <div className="ml-auto">
          <Link href={`/portfolios/${id}/risk`} className="bg-navy-900 hover:bg-navy-800 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm">
            Risk Analizi
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm">
          <div className="text-sm text-navy-700/70 font-medium mb-1 flex items-center gap-2">
             Toplam Değer
          </div>
          <div className="text-2xl font-bold text-navy-900">
            {summary.total_market_value != null ? `${Number(summary.total_market_value).toLocaleString('tr-TR')} ₺` : 'Yetersiz Veri'}
          </div>
        </div>
        <div className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm">
          <div className="text-sm text-navy-700/70 font-medium mb-1">
             Gerçekleşen K/Z
          </div>
          <div className={`text-2xl font-bold ${Number(summary.total_realized_pnl) > 0 ? 'text-success-600' : Number(summary.total_realized_pnl) < 0 ? 'text-danger-600' : 'text-slate-700'}`}>
            {Number(summary.total_realized_pnl) > 0 ? '+' : ''}{Number(summary.total_realized_pnl).toLocaleString('tr-TR')} ₺
          </div>
        </div>
        <div className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm">
          <div className="text-sm text-navy-700/70 font-medium mb-1">
             Gerçekleşmeyen K/Z
          </div>
          <div className={`text-2xl font-bold ${summary.total_unrealized_pnl != null ? (Number(summary.total_unrealized_pnl) > 0 ? 'text-success-600' : Number(summary.total_unrealized_pnl) < 0 ? 'text-danger-600' : 'text-slate-700') : 'text-slate-700'}`}>
             {summary.total_unrealized_pnl != null ? `${Number(summary.total_unrealized_pnl) > 0 ? '+' : ''}${Number(summary.total_unrealized_pnl).toLocaleString('tr-TR')} ₺` : 'Yetersiz Veri'}
          </div>
        </div>
        <div className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm">
          <div className="text-sm text-navy-700/70 font-medium mb-1">
             Yatırılan / Çekilen
          </div>
          <div className="text-lg font-bold text-slate-700">
             +{Number(summary.total_deposits).toLocaleString('tr-TR')} / -{Number(summary.total_withdrawals).toLocaleString('tr-TR')}
          </div>
        </div>
      </div>

      <div className="bg-surface rounded-xl border border-navy-800/10 shadow-sm overflow-hidden mt-6">
        <div className="p-5 border-b border-navy-800/10 flex justify-between items-center">
          <h2 className="text-lg font-bold text-navy-900">Açık Pozisyonlar</h2>
          <div className="text-xs text-slate-500 font-medium">
            Veri Durumu: {summary.market_data_freshness === 'DELAYED' ? 'Gecikmeli' : summary.market_data_freshness === 'STALE' ? 'Eksik / Güncel Değil' : summary.market_data_freshness}
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
            <table className="w-full text-left text-sm">
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
                    <td className="px-5 py-4 text-right font-medium">{Number(pos.quantity).toLocaleString('tr-TR')}</td>
                    <td className="px-5 py-4 text-right text-slate-600">{Number(pos.average_cost).toLocaleString('tr-TR')} ₺</td>
                    <td className="px-5 py-4 text-right font-medium">
                      {pos.current_price != null ? `${Number(pos.current_price).toLocaleString('tr-TR')} ₺` : 'Yetersiz Veri'}
                    </td>
                    <td className="px-5 py-4 text-right font-medium">
                      {pos.market_value != null ? `${Number(pos.market_value).toLocaleString('tr-TR')} ₺` : 'Yetersiz Veri'}
                    </td>
                    <td className="px-5 py-4 text-right">
                      {pos.unrealized_pnl != null ? (
                        <span className={`font-semibold ${Number(pos.unrealized_pnl) > 0 ? 'text-success-600' : Number(pos.unrealized_pnl) < 0 ? 'text-danger-600' : 'text-slate-600'}`}>
                          {Number(pos.unrealized_pnl) > 0 ? '+' : ''}{Number(pos.unrealized_pnl).toLocaleString('tr-TR')} ₺
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
    </div>
  );
}

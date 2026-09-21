"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { PositionLifecycleDTO } from "@/types/lifecycle";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { fetchApi } from "@/lib/api";
import { ArrowLeft, AlertCircle, DollarSign, Plus, LayoutDashboard, Briefcase, ShieldAlert, History } from "lucide-react";
import { useState } from "react";
import { PortfolioActionModal } from "@/components/PortfolioActionModal";
import PositionLifecycleRow from "@/components/PositionLifecycleRow";
import { PortfolioCharts } from "@/components/PortfolioCharts";
import { PortfolioRiskPanel } from "@/components/PortfolioRiskPanel";
import { PortfolioTransactions } from "@/components/PortfolioTransactions";
import { formatTry, formatMoney, formatQuantity, getProfitLossColorClass } from "@/lib/financialUi";
import { DataStateBadge } from "@/components/DataStateBadge";
import { BasketBuilder } from "@/components/BasketBuilder";

export default function PortfolioDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const router = useRouter();
  const searchParams = useSearchParams();
  const currentTab = searchParams.get("tab") || "genel";
  
  const [isActionModalOpen, setIsActionModalOpen] = useState(false);
  const [actionModalSymbol, setActionModalSymbol] = useState<string | undefined>(undefined);
  const [actionModalQuantity, setActionModalQuantity] = useState<number | undefined>(undefined);
  const [actionModalAction, setActionModalAction] = useState<any>(undefined);

  const openActionModal = (action?: any, symbol?: string, qty?: number) => {
    setActionModalQuantity(qty);
    setActionModalAction(action);
    setActionModalSymbol(symbol);
    setIsActionModalOpen(true);
  };
  const [modalInitialSymbol, setModalInitialSymbol] = useState("");
  const [modalInitialQuantity, setModalInitialQuantity] = useState<number | undefined>();
  const [modalInitialAction, setModalInitialAction] = useState<"BUY" | "SELL" | undefined>();

  const handleActionClick = (symbol: string, quantity: number, actionType: "BUY" | "SELL") => {
    setModalInitialSymbol(symbol);
    setModalInitialQuantity(quantity);
    setModalInitialAction(actionType);
    setIsActionModalOpen(true);
  };

  const { data: summary, isLoading, isError, error } = useQuery<any>({
    queryKey: ["portfolio", id, "summary"],
    queryFn: () => fetchApi(`/api/v1/portfolios/${id}/summary`),
    retry: 1,
  });

  const queryClient = useQueryClient();
  const { data: lifecycle, isFetching: isLifecycleFetching } = useQuery<PositionLifecycleDTO[]>({
    queryKey: ["portfolio", id, "lifecycle"],
    queryFn: () => fetchApi(`/api/v1/portfolios/${id}/lifecycle`),
    retry: 1,
  });

  const evaluateMutation = useMutation({
    mutationFn: () => fetchApi(`/api/v1/portfolios/${id}/lifecycle/evaluate`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolio", id, "lifecycle"] });
    },
  });

  const { data: portfolios } = useQuery<any[]>({
    queryKey: ["portfolios"],
    queryFn: () => fetchApi("/api/v1/portfolios"),
  });
  
  const portfolio = portfolios?.find((p: any) => String(p.id) === id);

  const tabs = [
    { id: "genel", label: "Genel Bakış", icon: LayoutDashboard },
    { id: "pozisyonlar", label: "Açık Pozisyonlar", icon: Briefcase },
    { id: "risk", label: "Risk Analizi", icon: ShieldAlert },
    { id: "islemler", label: "İşlem Geçmişi", icon: History },
    { id: "sepet", label: "Sepet Oluştur", icon: Briefcase },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px] text-slate-500">
        Portföy yükleniyor...
      </div>
    );
  }

  if (isError || !summary) {
    return (
      <div className="text-center py-12 flex flex-col items-center gap-4">
        <AlertCircle className="text-danger-500" size={32} />
        <div className="text-danger-700 font-medium">
          Portföy verileri alınamadı.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-7xl mx-auto pb-12">
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
          <button onClick={() => openActionModal()} className="flex-1 md:flex-none bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm flex items-center justify-center gap-2">
            <Plus size={16} /> Yeni İşlem
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm flex flex-col justify-between">
          <div className="text-sm text-navy-700/70 font-medium mb-1">
             Toplam Değer
          </div>
          <div className="text-2xl font-bold text-navy-900 tracking-tight whitespace-nowrap tabular-nums overflow-hidden text-ellipsis">
            {summary.total_market_value != null ? formatTry(summary.total_market_value) : 'Yetersiz Veri'}
          </div>
        </div>
        <div className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm flex flex-col justify-between">
          <div className="text-sm text-navy-700/70 font-medium mb-1">
             Gerçekleşen K/Z
          </div>
          <div className={`text-2xl font-bold tracking-tight whitespace-nowrap tabular-nums overflow-hidden text-ellipsis ${getProfitLossColorClass(summary.total_realized_pnl)}`}>
            {Number(summary.total_realized_pnl) > 0 ? '+' : ''}{formatTry(summary.total_realized_pnl)}
          </div>
        </div>
        <div className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm flex flex-col justify-between">
          <div className="text-sm text-navy-700/70 font-medium mb-1">
             Gerçekleşmeyen K/Z
          </div>
          <div className={`text-2xl font-bold tracking-tight whitespace-nowrap tabular-nums overflow-hidden text-ellipsis ${summary.total_unrealized_pnl != null ? getProfitLossColorClass(summary.total_unrealized_pnl) : 'text-slate-700'}`}>
             {summary.total_unrealized_pnl != null ? `${Number(summary.total_unrealized_pnl) > 0 ? '+' : ''}${formatTry(summary.total_unrealized_pnl)}` : 'Yetersiz Veri'}
          </div>
        </div>
        <div className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm flex flex-col justify-between">
          <div className="text-sm text-navy-700/70 font-medium mb-1">
             Yatırılan / Çekilen
          </div>
          <div className="text-lg font-bold flex flex-wrap gap-x-1.5 gap-y-0 items-baseline">
             <span className="text-emerald-600 whitespace-nowrap tabular-nums">+{formatTry(summary.total_deposits)}</span> 
             <span className="text-slate-300">/</span> 
             <span className="text-rose-600 whitespace-nowrap tabular-nums">-{formatTry(summary.total_withdrawals)}</span>
          </div>
        </div>
      </div>

      <div className="border-b border-navy-800/10">
        <nav className="flex space-x-6 overflow-x-auto" aria-label="Tabs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = currentTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => router.push(`/portfolios/${id}?tab=${tab.id}`)}
                className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
                  isActive
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
              >
                <Icon size={18} />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      <div className="mt-6">
        {currentTab === 'genel' && (
          <div className="space-y-6">
            <PortfolioCharts portfolioId={id} summary={summary} />
          </div>
        )}

        {currentTab === 'pozisyonlar' && (
          <div className="bg-surface rounded-xl border border-navy-800/10 shadow-sm overflow-hidden">
            <div className="p-5 border-b border-navy-800/10 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-2">
              <h2 className="text-lg font-bold text-navy-900">Açık Pozisyonlar</h2>
              <div className="flex items-center gap-4 text-xs font-medium">
                <div className="flex items-center gap-2">
                  <span className="text-slate-500">Veri Durumu:</span>
                  <DataStateBadge state={summary.market_data_freshness} />
                </div>
                <button 
                  onClick={() => evaluateMutation.mutate()}
                  disabled={evaluateMutation.isPending || isLifecycleFetching}
                  className="bg-primary-50 text-primary-700 hover:bg-primary-100 px-3 py-1.5 rounded-md transition-colors border border-primary-200 disabled:opacity-50 font-semibold"
                >
                  {evaluateMutation.isPending || isLifecycleFetching ? "Güncelleniyor..." : "Yaşam Döngüsünü Güncelle"}
                </button>
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
                        <th className="px-5 py-3 text-right">Varlık Sınıfı</th>
                        <th className="px-5 py-3 text-right">Adet</th>
                        <th className="px-5 py-3 text-right">Piyasa Değeri (TRY)</th>
                        <th className="px-5 py-3 text-right">K/Z</th>
                        <th className="px-5 py-3 text-center">Durum</th>
                        <th className="px-5 py-3 text-center">Öneri</th>
                        <th className="px-5 py-3 text-right">Son Değerlendirme</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {summary.positions.map((pos: any) => (
                      <PositionLifecycleRow 
                        key={pos.instrument_id} 
                        pos={pos} 
                        lc={lifecycle?.find((l: any) => l.instrument_id === pos.instrument_id)} 
                        isPaper={portfolio?.portfolio_type === "PAPER"}
                        onOpenActionModal={(action, p, qty) => openActionModal(action, p.symbol, qty)}
                      />
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {currentTab === 'risk' && (
          <PortfolioRiskPanel portfolioId={id} />
        )}

        {currentTab === 'islemler' && (
          <div className="bg-surface rounded-xl border border-navy-800/10 shadow-sm overflow-hidden">
            <PortfolioTransactions portfolioId={id} />
          </div>
        )}
        {currentTab === 'sepet' && (
          <div className="bg-surface rounded-xl border border-navy-800/10 shadow-sm overflow-hidden p-6">
             <h2 className="text-xl font-bold text-navy-900 mb-4">Sepet Oluştur (Basket Builder)</h2>
             <div>
               <BasketBuilder portfolioId={Number(id)} />
             </div>
          </div>
        )}
      </div>

      {isActionModalOpen && (
        <PortfolioActionModal 
          portfolioId={id} 
          isOpen={isActionModalOpen} 
          onClose={() => {
            setIsActionModalOpen(false);
            queryClient.invalidateQueries({ queryKey: ["portfolio", id] });
          }} 
          summary={summary}
          initialSymbol={actionModalSymbol}
          initialQuantity={actionModalQuantity}
          initialAction={actionModalAction}
          isPaper={portfolio?.portfolio_type === "PAPER"}
        />
      )}
    </div>
  );
}

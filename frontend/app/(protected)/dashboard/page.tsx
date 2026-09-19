"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { 
  WifiOff, 
  Briefcase, 
  Target, 
  ArrowRight,
  AlertCircle
} from "lucide-react";
import { useNetwork } from "@/components/NetworkProvider";
import { fetchApi } from "@/lib/api";
import { formatTry, formatActionLabel, getActionColorClass } from "@/lib/financialUi";
import { PortfolioOverviewDTO } from "@/lib/types";
import { InstrumentSearch } from "@/components/InstrumentSearch";
import type { OpportunityListResult } from "@/types/opportunity";

function OpportunityPreviewCard({ opp }: { opp: OpportunityListResult }) {
  const action = opp.personal_action || opp.market_view;
  const isMissing = opp.missing_data || opp.data_quality_score < 50;

  return (
    <Link href={`/instruments/${opp.symbol}`} className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-bold text-navy-900 text-lg">{opp.symbol}</h3>
          <p className="text-sm text-navy-700/60 truncate max-w-[140px]">{opp.name || opp.symbol}</p>
        </div>
        <span className={`px-2 py-1 text-xs font-bold rounded border ${getActionColorClass(action, isMissing)}`}>
          {formatActionLabel(action, isMissing)}
        </span>
      </div>
      
      <div>
        <div className="text-2xl font-semibold text-navy-900 mb-1">
          {formatTry(opp.quote_price)}
        </div>
        <div className="text-sm text-navy-700 mt-2">
          Piyasa Puanı: <span className="font-medium">{opp.market_score != null ? Number(opp.market_score).toFixed(0) : "—"}</span>
        </div>
      </div>
    </Link>
  );
}

export default function Dashboard() {
  const { isOnline } = useNetwork();
  
  const { 
    data: portfoliosData, 
    isLoading: isPortfoliosLoading, 
    isError: isPortfoliosError,
    error: portfoliosError,
    refetch: refetchPortfolios 
  } = useQuery({
    queryKey: ["portfolios"],
    queryFn: (): Promise<PortfolioOverviewDTO[]> => fetchApi('/api/v1/portfolios'),
  });

  const { data: oppsData, isLoading: isOppsLoading, isError: isOppsError } = useQuery({
    queryKey: ["dashboard_opportunities"],
    queryFn: () => fetchApi<OpportunityListResult[]>('/api/v1/opportunities'),
    staleTime: 60000,
  });

  // Preserve the backend's market-score ordering for the general preview.
  const topOpportunities = React.useMemo(() => {
    if (!Array.isArray(oppsData)) return [];
    return oppsData.slice(0, 3);
  }, [oppsData]);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-navy-900 tracking-tight">Günlük Özet</h1>
          <p className="text-navy-700 mt-1">Piyasalar ve portföy durumunuz.</p>
        </div>
        
        {!isOnline && (
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-2 rounded-lg flex items-center gap-2 shadow-sm shrink-0">
            <WifiOff size={18} />
            <span className="text-sm font-medium">Çevrimdışı (Eski Veri)</span>
          </div>
        )}
      </div>

      <div className="w-full">
        <InstrumentSearch />
      </div>

      {/* Portfolios Overview Section */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-navy-900 flex items-center gap-2">
            <Briefcase className="text-primary-600" size={20} />
            Portföylerim
          </h2>
          <Link href="/portfolios" className="text-sm font-medium text-primary-600 hover:text-primary-700 flex items-center gap-1">
            Tümünü Gör <ArrowRight size={16} />
          </Link>
        </div>
        
        {isPortfoliosLoading ? (
          <div className="h-32 bg-slate-100 animate-pulse rounded-xl border border-slate-200"></div>
        ) : isPortfoliosError ? (
          <div className="bg-red-50 text-red-600 rounded-xl p-5 border border-red-200 flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm">
              <AlertCircle size={18} />
              <span>
                {(portfoliosError as any)?.name === 'RequestTimeoutError' ? 'Portföy verileri zamanında alınamadı.' :
                 (portfoliosError as any)?.name === 'NetworkError' ? 'Portföy servisine şu anda ulaşılamıyor.' :
                 'Portföy verileri alınırken sunucu hatası oluştu.'}
              </span>
            </div>
            <button onClick={() => refetchPortfolios()} className="text-sm font-medium bg-white px-3 py-1.5 rounded text-red-700 hover:bg-red-100 transition border border-red-200">
              Tekrar Dene
            </button>
          </div>
        ) : (portfoliosData?.length || 0) > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {portfoliosData!.map((p: PortfolioOverviewDTO) => (
              <div key={p.id} className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm">
                <h3 className="font-semibold text-navy-900">{p.name}</h3>
                <p className="text-sm text-navy-700/60 mb-3">{p.portfolio_type === 'REAL' ? 'Gerçek' : 'Simülasyon'}</p>
                <div className="text-2xl font-bold text-navy-900 tracking-tight whitespace-nowrap tabular-nums overflow-hidden text-ellipsis" title={p.total_market_value != null ? formatTry(p.total_market_value) : '0,00 ₺'}>
                  {p.total_market_value != null ? formatTry(p.total_market_value) : '0,00 ₺'}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-surface rounded-xl p-8 border border-navy-800/10 text-center shadow-sm">
            <p className="text-navy-700 mb-4">Henüz bir portföy oluşturmadınız.</p>
            <Link href="/portfolios" className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
              Portföy Oluştur
            </Link>
          </div>
        )}
      </section>

      {/* Opportunities Snapshot Section */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-navy-900 flex items-center gap-2">
            <Target className="text-primary-600" size={20} />
            Güncel Fırsatlar
          </h2>
          <Link href="/opportunities" className="text-sm font-medium text-primary-600 hover:text-primary-700 flex items-center gap-1">
            Tüm Fırsatları Gör <ArrowRight size={16} />
          </Link>
        </div>

        {isOppsLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map(i => <div key={i} className="h-32 bg-slate-100 animate-pulse rounded-xl border border-slate-200"></div>)}
          </div>
        ) : isOppsError ? (
          <div className="bg-red-50 text-red-600 rounded-xl p-5 border border-red-200 text-sm flex items-center gap-2">
            <AlertCircle size={18} /> Fırsatlar yüklenemedi.
          </div>
        ) : topOpportunities.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {topOpportunities.map((opp) => (
              <OpportunityPreviewCard key={opp.symbol} opp={opp} />
            ))}
          </div>
        ) : (
          <div className="bg-surface rounded-xl p-6 border border-navy-800/10 text-center shadow-sm text-sm text-slate-500">
            Şu anda yeterli veri bulunamadı.
          </div>
        )}
      </section>
    </div>
  );
}

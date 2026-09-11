"use client";
import React from "react";



import { useQuery } from "@tanstack/react-query";

import Link from "next/link";

import { 

  Activity, 

  WifiOff, 

  Briefcase, 

  TrendingUp, 

  TrendingDown, 

  Clock, 

  AlertCircle,

  ArrowRight

} from "lucide-react";

import { useNetwork } from "@/components/NetworkProvider";

import { fetchApi } from "@/lib/api";

import { DataStateBadge } from "@/components/DataStateBadge";

import { formatTry } from "@/lib/financialUi";
import { QuoteDTO, PortfolioOverviewDTO } from "@/lib/types";



function QuoteCard({ symbol, name }: { symbol: string; name: string }) {

  const { isOnline } = useNetwork();

  const { data: quote, isLoading, isError } = useQuery<QuoteDTO>({

    queryKey: ["quote", symbol],

    queryFn: () => fetchApi(`/api/v1/instruments/${symbol}/quote`),

    refetchInterval: isOnline ? 30000 : false,

  });



  return (

    <Link href={`/instruments/${symbol}`} className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">

      <div className="flex justify-between items-start mb-4">

        <div>

          <h3 className="font-bold text-navy-900 text-lg">{symbol}</h3>

          {name !== symbol && <p className="text-sm text-navy-700/60 truncate max-w-[140px]">{name}</p>}

        </div>

        {Boolean(quote) && (

          <span className={`px-2 py-0.5 text-xs font-semibold rounded-full border ${

            quote?.data_state === "DELAYED" ? "bg-yellow-50 text-yellow-700 border-yellow-200" :

            quote?.data_state === "EOD" ? "bg-slate-50 text-slate-600 border-slate-200" :

            "bg-primary-50 text-primary-700 border-primary-200"

          }`}>

            {quote?.data_state || "DELAYED"}

          </span>

        )}

      </div>



      {isLoading ? (

        <div className="animate-pulse space-y-2">

          <div className="h-6 bg-slate-200 rounded w-1/2"></div>

          <div className="h-4 bg-slate-200 rounded w-1/3"></div>

        </div>

      ) : isError ? (

        <div className="text-danger-500 text-sm flex items-center gap-1">

          <AlertCircle size={14} /> Veri alınamadı

        </div>

      ) : quote ? (

        <div>

          <div className="text-2xl font-semibold text-navy-900 mb-1">

            {Number(quote?.price).toFixed(2)} ₺

          </div>

          <div className={`text-sm font-medium flex items-center gap-1 ${

            Number(quote?.change_pct) >= 0 ? "text-success-600" : "text-danger-600"

          }`}>

            {Number(quote?.change_pct) >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}

            {Number(quote?.change_pct) >= 0 ? "+" : ""}

            {Number(quote?.change_pct).toFixed(2)}%

          </div>

        </div>

      ) : null}

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



  const { data: instrumentsData, isLoading: isInstrumentsLoading, isError: isInstrumentsError } = useQuery({

    queryKey: ["dashboard_instruments"],

    queryFn: () => fetchApi('/api/v1/instruments?size=4'),

  });



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



      {/* Markets Snapshot Section */}

      <section className="space-y-4">

        <div className="flex items-center justify-between">

          <h2 className="text-xl font-semibold text-navy-900 flex items-center gap-2">

            <Activity className="text-primary-600" size={20} />

            BIST 100 Gözlem

          </h2>

          <Link href="/markets" className="text-sm font-medium text-primary-600 hover:text-primary-700 flex items-center gap-1">

            Tüm Piyasalar <ArrowRight size={16} />

          </Link>

        </div>



        {isInstrumentsLoading ? (

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

            {[1, 2, 3, 4].map(i => <div key={i} className="h-32 bg-slate-100 animate-pulse rounded-xl border border-slate-200"></div>)}

          </div>

        ) : isInstrumentsError ? (

          <div className="bg-red-50 text-red-600 rounded-xl p-5 border border-red-200 text-sm flex items-center gap-2">

            <AlertCircle size={18} /> Gözlem listesi yüklenemedi.

          </div>

        ) : (

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

            {(instrumentsData as any)?.items?.map((inst: any) => (

              <QuoteCard key={inst.symbol} symbol={inst.symbol} name={inst.name} />

            ))}

          </div>

        )}

      </section>

    </div>

  );

}


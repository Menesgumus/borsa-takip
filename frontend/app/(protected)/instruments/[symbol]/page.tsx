"use client";

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { fetchApi } from '@/lib/api';
import Link from 'next/link';
import { ArrowLeft, Clock, AlertCircle } from 'lucide-react';
import { useNetwork } from '@/components/NetworkProvider';
import dynamic from 'next/dynamic';
import { DataStateBadge } from '@/components/DataStateBadge';

const CandlestickChart = dynamic(() => import('@/components/CandlestickChart'), { ssr: false });
const DecisionCard = dynamic(() => import('@/components/DecisionCard'), { ssr: false });

export default function InstrumentDetail() {
  const params = useParams();
  const symbol = params.symbol as string;
  const { isOnline } = useNetwork();
  
  const [period, setPeriod] = useState('1Y');
  const [activeTab, setActiveTab] = useState('GENEL_BAKIS');

  const { data: instrument, isLoading: isInstrumentLoading } = useQuery({
    queryKey: ['instrument', symbol, 'basic'],
    queryFn: () => fetchApi(`/api/v1/instruments/${symbol}`),
  });

  // 1. Fetch Context (Live Quote etc)
  const { data: context, isLoading: isContextLoading } = useQuery({
    queryKey: ['instrument', symbol, 'context'],
    queryFn: () => fetchApi(`/api/v1/instruments/${symbol}/context`),
    refetchInterval: isOnline ? 30000 : false,
  });

  const { data: quote } = useQuery({
    queryKey: ['instrument', symbol, 'quote'],
    queryFn: () => fetchApi(`/api/v1/instruments/${symbol}/quote`),
    refetchInterval: isOnline ? 10000 : false,
  });

  // 2. Fetch History
  const { data: history, isLoading: isHistoryLoading, isError: isHistoryError } = useQuery({
    queryKey: ['instrument', symbol, 'history', period],
    queryFn: () => fetchApi(`/api/v1/instruments/${symbol}/history?period=${period}`),
    enabled: isOnline,
  });

  // 3. Fetch Technical
  const { data: technical } = useQuery({
    queryKey: ['instrument', symbol, 'technical'],
    queryFn: () => fetchApi(`/api/v1/instruments/${symbol}/technical`),
  });

  // 4. Fetch Decision
  const { data: decision } = useQuery({
    queryKey: ['instrument', symbol, 'decision'],
    queryFn: () => fetchApi(`/api/v1/instruments/${symbol}/decision`),
  });

  // 5. Fetch User Profile
  const { data: profile } = useQuery({
    queryKey: ['user', 'me'],
    queryFn: () => fetchApi(`/api/v1/users/me`),
  });

  if (isContextLoading) {
    return <div className="animate-pulse space-y-4 p-4">Yükleniyor...</div>;
  }

  const q = quote as any;
  const inst = instrument as any;
  const hist = history as any;
  const tech = technical as any;
  const ctx = context as any;
  const dec = decision as any;

  const isPositive = q ? Number(q.change_pct) >= 0 : false;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Breadcrumb */}
      <nav className="flex items-center text-sm text-navy-700/60 mb-4">
        <Link href="/markets" className="hover:text-primary-600 transition-colors flex items-center gap-1">
          <ArrowLeft size={14} /> Piyasalar
        </Link>
        <span className="mx-2">/</span>
        <span className="font-medium text-navy-900">{symbol}</span>
      </nav>

      {/* Hero Header */}
      <div className="bg-surface rounded-xl p-6 border border-navy-800/10 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 className="text-3xl font-bold text-navy-900 tracking-tight">{symbol}</h1>
          {inst?.name && inst.name !== symbol && <p className="text-navy-700/80 text-lg mt-1">{inst.name}</p>}
          <div className="text-xs font-medium text-navy-700/60 mt-2 flex items-center gap-2">
            BIST &middot; STOCK
          </div>
        </div>

        <div className="text-left md:text-right">
          <div className="text-4xl font-bold text-navy-900">
            {quote ? `${Number(q.price).toFixed(2)} ₺` : '---'}
          </div>
          <div className={`text-lg font-medium flex items-center md:justify-end gap-1 mt-1 ${
            isPositive ? 'text-success-600' : 'text-danger-600'
          }`}>
            {isPositive ? '+' : ''}
            {quote ? `${(Number(q.price) - Number(q.previous_close)).toFixed(2)} (${Number(q.change_pct).toFixed(2)}%)` : '---'}
          </div>
          <div className="mt-3 flex flex-wrap md:justify-end gap-2 items-center text-xs">
            {Boolean(quote) && (
              <DataStateBadge state={q.data_state} />
            )}
            <span className="px-2 py-1 bg-slate-50 text-slate-600 border border-slate-200 rounded font-medium">
              Yahoo Finance
            </span>
            {Boolean(quote) && (
              <span className="text-navy-700/60 flex items-center gap-1">
                <Clock size={12} /> Son fiyat: {new Date((quote as any).timestamp).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })} (Gecikmeli)
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Chart Section */}
      <div className="bg-surface rounded-xl p-4 border border-navy-800/10 shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-navy-900">Fiyat Grafiği <span className="text-sm font-normal text-slate-500 ml-2">(Son günlük kapanış)</span></h2>
          <div className="flex bg-slate-100 rounded-lg p-1">
            {['1A', '3A', '6A', '1Y', '2Y'].map(p => {
              const mapped = p.replace('A', 'M').replace('Y', 'Y');
              return (
                <button
                  key={p}
                  onClick={() => setPeriod(mapped)}
                  className={`px-3 py-1 text-sm font-medium rounded-md transition-all ${
                    period === mapped ? 'bg-white text-primary-600 shadow-sm' : 'text-slate-500 hover:text-navy-900'
                  }`}
                >
                  {p}
                </button>
              )
            })}
          </div>
        </div>
        
        <div className="h-[400px] w-full border border-slate-100 rounded-lg overflow-hidden bg-slate-50 relative">
          {isHistoryLoading ? (
            <div className="absolute inset-0 flex items-center justify-center text-slate-400">Yükleniyor...</div>
          ) : isHistoryError ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-danger-500">
              <AlertCircle size={32} className="text-danger-300 mb-2" />
              <p>Veri çekilemedi.</p>
              <p className="text-xs mt-1 text-slate-500">Geçmiş veriler alınırken bir hata oluştu.</p>
            </div>
          ) : hist?.length > 0 ? (
            <CandlestickChart data={history as any} symbol={symbol} userId={(profile as any)?.email} />
          ) : (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500">
              <AlertCircle size={32} className="text-slate-300 mb-2" />
              <p>Grafik verisi bulunamadı.</p>
              <p className="text-xs mt-1">Bu sembol için belirtilen dönemde işlem verisi bulunmuyor.</p>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-navy-800/10">
        <nav className="flex space-x-6 overflow-x-auto">
          {[
            { id: 'GENEL_BAKIS', label: 'GENEL BAKIÅ' },
            { id: 'TEKNIK', label: 'TEKNİK' },
            { id: 'KARAR', label: 'KARAR' },
            { id: 'KAP', label: 'KAP / HABER' },
            { id: 'TEMEL', label: 'TEMEL' },
            { id: 'RISK', label: 'RİSK / PORTFÖY' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`pb-3 text-sm font-semibold whitespace-nowrap border-b-2 transition-colors ${
                activeTab === tab.id 
                  ? 'border-primary-600 text-primary-600' 
                  : 'border-transparent text-navy-700/60 hover:text-navy-900 hover:border-navy-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="py-4">
        {activeTab === 'GENEL_BAKIS' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm">
              <h3 className="text-sm font-semibold text-navy-700 mb-4">Özet Bilgiler</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-navy-700/70">Fiyat</span>
                  <span className="font-medium text-navy-900">{(quote as any)?.price ? `${Number((quote as any).price).toFixed(2)} ₺` : '-'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-navy-700/70">Değişim</span>
                  <span className={`font-medium ${isPositive ? 'text-success-600' : 'text-danger-600'}`}>
                    {(quote as any)?.change_pct ? `${Number((quote as any).change_pct).toFixed(2)}%` : '-'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-navy-700/70">Hacim</span>
                  <span className="font-medium text-navy-900">{(quote as any)?.volume ? Number((quote as any).volume).toLocaleString() : '-'}</span>
                </div>
              </div>
            </div>
            
            <div className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm">
              <h3 className="text-sm font-semibold text-navy-700 mb-4">Teknik Durum</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-navy-700/70">RSI (14)</span>
                  <span className="font-medium text-navy-900">
                    {tech?.indicators?.length > 0 && tech.indicators[tech.indicators.length - 1].rsi_14 != null
                      ? tech.indicators[tech.indicators.length - 1].rsi_14.toFixed(2)
                      : 'Yetersiz Veri'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-navy-700/70">MACD Trend</span>
                  <span className="font-medium text-navy-900">
                    {(() => {
                      if (!tech?.indicators || tech.indicators.length === 0) return 'Yetersiz Veri';
                      const macdVal = tech.indicators[tech.indicators.length - 1].macd_hist;
                      if (macdVal == null) return 'Yetersiz Veri';
                      return macdVal > 0 ? 'Pozitif' : (macdVal < 0 ? 'Negatif' : 'Nötr');
                    })()}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-surface rounded-xl p-5 border border-navy-800/10 shadow-sm">
              <h3 className="text-sm font-semibold text-navy-700 mb-4">Sistem Kararı</h3>
              {decision ? (
                <div className="text-center mt-6">
                  <div className={`inline-block px-4 py-2 rounded-lg font-bold text-lg mb-2 ${
                    (decision as any).decision_state === 'INSUFFICIENT_DATA' ? 'bg-yellow-50 text-yellow-700' :
                    ['STRONG_BUY', 'BUY'].includes((decision as any).market_view) ? 'bg-success-50 text-success-700' :
                    ['STRONG_SELL', 'SELL'].includes((decision as any).market_view) ? 'bg-danger-50 text-danger-700' :
                    'bg-slate-100 text-slate-700'
                  }`}>
                    {(decision as any).decision_state === 'INSUFFICIENT_DATA' ? 'YETERSİZ VERİ (BEKLE)' :
                     (decision as any).market_view === 'STRONG_BUY' ? 'GÜÇLÜ AL' : 
                     (decision as any).market_view === 'BUY' ? 'KADEMELİ AL' : 
                     (decision as any).market_view === 'HOLD' ? 'BEKLE' : 
                     (decision as any).market_view === 'SELL' ? 'KADEMELİ SAT' : 'SAT'}
                  </div>
                  <div className="text-sm text-navy-700/60 mt-2">Detaylar için KARAR sekmesine bakınız.</div>
                </div>
              ) : (
                <div className="text-sm text-slate-500 text-center mt-8">Hesaplanıyor...</div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'KARAR' && (
          <div className="max-w-3xl mx-auto">
            {decision ? (
              <DecisionCard decision={decision as any} symbol={symbol} />
            ) : (
              <div className="text-center p-8 bg-surface rounded-xl border border-navy-800/10 text-slate-500">
                Karar verisi bulunamadı veya hesaplanıyor.
              </div>
            )}
          </div>
        )}

        {activeTab === 'TEKNIK' && (
          <div className="bg-surface rounded-xl p-6 border border-navy-800/10 shadow-sm">
            <h3 className="text-lg font-semibold text-navy-900 mb-6">Teknik Göstergeler</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {tech?.indicators?.length > 0 ? (() => {
                const latest = tech.indicators[tech.indicators.length - 1];
                const formatVal = (val: number | null | undefined) => val != null ? val.toFixed(2) : 'Yetersiz Veri';
                
                return (
                  <>
                    <div className="flex flex-col border-b border-slate-100 pb-3">
                      <span className="text-xs font-medium text-navy-700/60">RSI (14)</span>
                      <span className="text-lg font-bold text-navy-900 mt-1">{formatVal(latest.rsi_14)}</span>
                      <span className="text-xs text-navy-700 mt-1">{latest.rsi_14 ? (latest.rsi_14 > 70 ? 'Aşırı Alım' : latest.rsi_14 < 30 ? 'Aşırı Satım' : 'Nötr') : ''}</span>
                    </div>
                    <div className="flex flex-col border-b border-slate-100 pb-3">
                      <span className="text-xs font-medium text-navy-700/60">SMA 20</span>
                      <span className="text-lg font-bold text-navy-900 mt-1">{formatVal(latest.sma_20)}</span>
                    </div>
                    <div className="flex flex-col border-b border-slate-100 pb-3">
                      <span className="text-xs font-medium text-navy-700/60">EMA 20</span>
                      <span className="text-lg font-bold text-navy-900 mt-1">{formatVal(latest.ema_20)}</span>
                    </div>
                    <div className="flex flex-col border-b border-slate-100 pb-3">
                      <span className="text-xs font-medium text-navy-700/60">MACD</span>
                      <span className="text-lg font-bold text-navy-900 mt-1">{formatVal(latest.macd_line)}</span>
                    </div>
                    <div className="flex flex-col border-b border-slate-100 pb-3">
                      <span className="text-xs font-medium text-navy-700/60">MACD Signal</span>
                      <span className="text-lg font-bold text-navy-900 mt-1">{formatVal(latest.macd_signal)}</span>
                    </div>
                    <div className="flex flex-col border-b border-slate-100 pb-3">
                      <span className="text-xs font-medium text-navy-700/60">MACD Histogram</span>
                      <span className="text-lg font-bold text-navy-900 mt-1">{formatVal(latest.macd_hist)}</span>
                    </div>
                  </>
                );
              })() : (
                <div className="col-span-3 text-center text-slate-500 py-8">Yetersiz veri.</div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'KAP' && (
          <div className="bg-surface rounded-xl p-6 border border-navy-800/10 shadow-sm">
            <h3 className="text-lg font-semibold text-navy-900 mb-6">KAP ve Haberler</h3>
            
            <div className="mb-8">
              <h4 className="text-sm font-bold text-navy-700 mb-3 border-b pb-2">KAP Bildirimleri</h4>
              {!(context as any)?.availability?.kap ? (
                <div className="text-slate-500 text-sm py-4">KAP veri kaynağı şu an ulaşılamıyor (UNAVAILABLE).</div>
              ) : (context as any)?.disclosures?.length > 0 ? (
                <ul className="space-y-3">
                  {(context as any).disclosures.map((d: any, idx: number) => (
                    <li key={idx} className="text-sm">
                      <span className="font-medium text-navy-900">{new Date(d.publish_date).toLocaleDateString()}</span> - <a href={d.url} target="_blank" className="text-primary-600 hover:underline">{d.title}</a>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-slate-500 text-sm py-4">Son KAP bildirimi bulunmuyor (EMPTY).</div>
              )}
            </div>

            <div>
              <h4 className="text-sm font-bold text-navy-700 mb-3 border-b pb-2">Piyasa Haberleri</h4>
              {!(context as any)?.availability?.news ? (
                <div className="text-slate-500 text-sm py-4">Haber kaynağı şu an ulaşılamıyor (NEWS_UNAVAILABLE).</div>
              ) : (context as any)?.news?.length > 0 ? (
                <ul className="space-y-3">
                  {(context as any).news.map((n: any, idx: number) => (
                    <li key={idx} className="text-sm">
                      <span className="font-medium text-navy-900">{new Date(n.publish_date).toLocaleDateString()}</span> - <a href={n.url} target="_blank" className="text-primary-600 hover:underline">{n.title}</a>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-slate-500 text-sm py-4">Güncel haber bulunmuyor.</div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'TEMEL' && (
          <div className="text-center p-12 bg-surface rounded-xl border border-navy-800/10">
            <h3 className="text-lg font-medium text-navy-900 mb-2">TEMEL VERİ KAYNAÄI BAÄLI DEÄİL</h3>
            <p className="text-navy-700/60">Bu modül (F/K, PD/DD, Bilanço) için ticari veri sağlayıcı entegrasyonu gerekmektedir.</p>
          </div>
        )}

        {activeTab === 'RISK' && (
          <div className="text-center p-12 bg-surface rounded-xl border border-navy-800/10">
            <h3 className="text-lg font-medium text-navy-900 mb-2">Bu hisseyi portföy riskinizle karşılaştırmak için bir portföy seçin.</h3>
            <p className="text-navy-700/60">Portföy seçimi sonrası algoritma ağırlık ve korelasyon hesaplayacaktır.</p>
          </div>
        )}
      </div>
    </div>
  );
}


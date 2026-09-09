"use client";

import React from 'react';
import { ShieldAlert, Activity, CheckCircle, Info } from 'lucide-react';

export default function DecisionCard({ decision, symbol }: { decision: any, symbol: string }) {
  
  const getMarketViewStyle = (view: string) => {
    switch (view) {
      case 'STRONG_BUY': return 'bg-success-50 border-success-200 text-success-700';
      case 'BUY': return 'bg-success-50 border-success-200 text-success-600';
      case 'HOLD': return 'bg-slate-50 border-slate-200 text-slate-700';
      case 'SELL': return 'bg-danger-50 border-danger-200 text-danger-600';
      case 'STRONG_SELL': return 'bg-danger-50 border-danger-200 text-danger-700';
      default: return 'bg-slate-50 border-slate-200 text-slate-600';
    }
  };

  const getLabel = (view: string, state?: string) => {
    if (state === 'INSUFFICIENT_DATA') return 'YETERSİZ VERİ (BEKLE)';
    switch (view) {
      case 'STRONG_BUY': return 'GÜÇLÜ AL';
      case 'BUY': return 'KADEMELİ AL';
      case 'HOLD': return 'BEKLE';
      case 'SELL': return 'KADEMELİ SAT';
      case 'STRONG_SELL': return 'SAT';
      default: return view || 'BİLİNMİYOR';
    }
  };

  // Translate reason codes to Turkish
  const translateReason = (code: string) => {
    const map: Record<string, string> = {
      'RSI_OVERSOLD': 'RSI düşük bölgede (Aşırı satım)',
      'RSI_OVERBOUGHT': 'RSI yüksek bölgede (Aşırı alım)',
      'MACD_BULLISH': 'MACD pozitif trende girdi',
      'MACD_BEARISH': 'MACD negatif trende girdi',
      'PRICE_ABOVE_SMA200': 'Fiyat uzun vadeli ortalamanın (SMA200) üzerinde',
      'PRICE_BELOW_SMA200': 'Fiyat uzun vadeli ortalamanın altında',
      'RISK_LIMIT_EXCEEDED': 'Portföy konsantrasyon riski yüksek',
      'LOW_DATA_QUALITY': 'Veri kalitesi hesaplama için yetersiz',
      'INSUFFICIENT_DATA': 'Grafik geçmişi veya temel veriler yetersiz',
      'NEWS_UNAVAILABLE': 'Haber verisi şu anda kullanılamıyor',
    };
    return map[code] || code;
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Market View */}
        <div className={`p-6 rounded-xl border ${getMarketViewStyle(decision.market_view)} flex flex-col items-center justify-center text-center shadow-sm`}>
          <span className="text-sm font-semibold uppercase tracking-wider mb-2 opacity-80">Piyasa Görünümü</span>
          <span className="text-3xl font-bold">{getLabel(decision.market_view, decision.decision_state)}</span>
        </div>

        {/* Personal Action */}
        <div className={`p-6 rounded-xl border ${decision.personal_action ? getMarketViewStyle(decision.personal_action) : 'bg-surface border-navy-800/10 text-navy-900'} flex flex-col items-center justify-center text-center shadow-sm`}>
          <span className="text-sm font-semibold uppercase tracking-wider mb-2 opacity-80">Kişisel Aksiyon</span>
          <span className="text-3xl font-bold">
            {decision.personal_action ? getLabel(decision.personal_action, decision.decision_state) : 'DEĞERLENDİRİLMEDİ'}
          </span>
          {!decision.personal_action && (
            <span className="text-xs mt-2 opacity-60">Portföyünüzde bulunmuyor veya risk profili yok.</span>
          )}
        </div>
      </div>

      <div className="bg-surface rounded-xl p-6 border border-navy-800/10 shadow-sm">
        <h3 className="font-semibold text-navy-900 mb-4 flex items-center gap-2">
          <Activity size={18} className="text-primary-600" /> Neden Bu Karar Verildi?
        </h3>
        
        <ul className="space-y-3">
          {decision.reason_codes?.map((code: string) => (
            <li key={code} className="flex items-start gap-2">
              <CheckCircle className="text-success-500 mt-0.5 shrink-0" size={16} />
              <span className="text-navy-800 text-sm">{translateReason(code)}</span>
            </li>
          )) || <li className="text-sm text-navy-700/60">Belirli bir neden kodu üretilmedi.</li>}
          
          {decision.warnings?.map((warn: string) => (
            <li key={warn} className="flex items-start gap-2">
              <ShieldAlert className="text-yellow-500 mt-0.5 shrink-0" size={16} />
              <span className="text-navy-800 text-sm">Uyarı: {translateReason(warn)}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
          <span className="text-xs text-slate-500 block">Genel Puan</span>
          <span className="font-bold text-navy-900 text-lg">
            {Number(decision.overall_market_score || 0).toFixed(1)} / 100
          </span>
        </div>
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
          <span className="text-xs text-slate-500 block">Piyasa/Teknik Veri Kalitesi</span>
          <span className="font-bold text-navy-900 text-lg">
            {Number(decision.data_quality_score || 0).toFixed(1)} / 100
          </span>
        </div>
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
          <span className="text-xs text-slate-500 block">Durum</span>
          <span className="font-bold text-navy-900 text-sm mt-1 block truncate">
            {decision.decision_state || 'AVAILABLE'}
          </span>
        </div>
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
          <span className="text-xs text-slate-500 block">Hesaplama Tarihi</span>
          <span className="font-medium text-navy-900 text-sm mt-1 block">
            {new Date(decision.as_of).toLocaleTimeString('tr-TR')}
          </span>
        </div>
      </div>
    </div>
  );
}

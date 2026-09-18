"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams, useSearchParams } from "next/navigation";
import Link from "next/link";
import { fetchApi } from "@/lib/api";
import { ArrowLeft, Target, ShieldAlert, Star, Activity, Briefcase, FileText, TrendingUp, AlertTriangle } from "lucide-react";
import { OpportunityDetailResult } from "@/types/opportunity";
import { formatTry, formatPercent, formatActionLabel, getActionColorClass, formatQuantity, translateSizingState, translateSizingReason } from "@/lib/financialUi";
import { DataStateBadge } from "@/components/DataStateBadge";
import { useState } from "react";
import { PortfolioActionModal } from "@/components/PortfolioActionModal";
import { CheckCircle } from "lucide-react";

const translateReason = (reason: string) => {
  const map: Record<string, string> = {
    "MACD_BULLISH": "MACD Yükseliş Trendinde (Golden Cross)",
    "RSI_OVERSOLD": "RSI Aşırı Satış Bölgesinde (Alım fırsatı olabilir)",
    "RSI_OVERBOUGHT": "RSI Aşırı Alım Bölgesinde",
    "TREND_UP_GOLDEN": "Hareketli Ortalamalar Yükseliş Eğiliminde",
    "TREND_DOWN_DEATH": "Hareketli Ortalamalar Düşüş Eğiliminde",
    "RISK_LIMIT_EXCEEDED": "Portföy Risk Limitleri Aşıldı",
    "INSUFFICIENT_DATA": "Yetersiz Veri",
    "STRONG_FUNDAMENTALS": "Güçlü Temel Göstergeler",
    "POSITIVE_NEWS": "Olumlu Haber Akışı",
    "FAVORABLE_RISK_REWARD": "Uygun Risk/Getiri Oranı",
    "DELAYED_MARKET_DATA": "Gecikmeli Piyasa Verisi Kullanıldı",
    "MARKET_CONDITIONS_FAVORABLE": "Olumlu Piyasa Koşulları",
    "PORTFOLIO_FIT_HIGH": "Portföy Risk/Getiri Beklentinizle Yüksek Uyum",
    "CONCENTRATION_LIMIT_OK": "Portföy Yoğunluk Sınırı İçinde"
  };
  return map[reason] || reason;
};

const translateWarning = (warning: string) => {
  const map: Record<string, string> = {
    "NEWS_UNAVAILABLE": "Haber verisi bulunamadı",
    "STALE_MARKET_DATA": "Güncel olmayan piyasa verisi",
    "PORTFOLIO_CONCENTRATION_LIMIT": "Portföy yoğunluk sınırına yaklaşıldı veya aşıldı",
    "HIGH_VOLATILITY": "Yüksek volatilite uyarısı",
    "NO_TECHNICAL_DATA": "Teknik analiz verisi yetersiz"
  };
  return map[warning] || warning;
};

export default function OpportunityDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const symbol = params.symbol as string;
  const portfolioIdParam = searchParams.get("portfolio_id");
  const portfolioId = portfolioIdParam ? Number(portfolioIdParam) : null;

  const [isTradeModalOpen, setIsTradeModalOpen] = useState(false);

  const { data: inst, isLoading, isError } = useQuery({
    queryKey: ["opportunity-detail", symbol, portfolioId],
    queryFn: async () => {
      const url = portfolioId 
        ? `/api/v1/opportunities/${symbol}?portfolio_id=${portfolioId}`
        : `/api/v1/opportunities/${symbol}`;
      return fetchApi(url) as Promise<OpportunityDetailResult>;
    },
  });

  if (isLoading) {
    return <div className="p-12 text-center text-slate-500 animate-pulse">Fırsat detayı yükleniyor...</div>;
  }

  if (isError || !inst) {
    return (
      <div className="max-w-4xl mx-auto mt-10 bg-red-50 text-red-600 rounded-xl p-6 border border-red-200 flex flex-col items-center gap-4">
        <ShieldAlert size={32} />
        <div className="font-medium text-lg">Bu fırsat şu an aktif değil veya bulunamadı.</div>
        <Link href="/opportunities" className="text-sm font-bold text-red-700 underline">Fırsatlara Dön</Link>
      </div>
    );
  }

  const action = inst.personal_action || inst.market_view;
  const isMissing = inst.missing_data || inst.data_quality_score < 50;

  const getScoreDisplay = (score: number | null) => {
    return score !== null ? Number(score).toFixed(0) : "Veri Yok";
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-4xl mx-auto">
      <Link href="/opportunities" className="inline-flex items-center text-sm font-medium text-navy-600 hover:text-primary-600 mb-2">
        <ArrowLeft size={16} className="mr-1" />
        Fırsatlara Dön
      </Link>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-3xl font-bold text-navy-900">{inst.symbol}</h1>
              <span className={`px-3 py-1 text-sm font-bold rounded border ${getActionColorClass(action, isMissing)}`}>
                {formatActionLabel(action, isMissing)}
              </span>
            </div>
            <p className="text-navy-600 font-medium">{inst.name || "Hisse Senedi"}</p>
          </div>
          <div className="flex flex-col items-start sm:items-end gap-2 bg-slate-50 p-4 rounded-lg border border-slate-100 w-full sm:w-auto">
            <div className="text-sm text-slate-500 font-medium">Anlık Fiyat</div>
            <div className="text-2xl font-bold text-navy-900 flex items-center gap-2">
              {formatTry(inst.quote_price)}
              {inst.quote_data_state && <DataStateBadge state={inst.quote_data_state} />}
            </div>
            {inst.quote_as_of && (
               <div className="text-xs text-slate-400">
                 Güncellenme: {new Date(inst.quote_as_of).toLocaleTimeString('tr-TR')}
               </div>
            )}
          </div>
        </div>

        {/* Action Button if actionable */}
        {portfolioId && inst.sizing_state === "OK" && !isMissing && (
          <div className="bg-primary-50 p-4 border-b border-primary-100 flex justify-between items-center">
            <div>
              <div className="text-sm text-primary-800 font-medium mb-1">Önerilen Aksiyon</div>
              <div className="font-bold text-primary-900">
                {inst.recommended_quantity} adet {inst.symbol} Alımı ({formatTry(inst.recommended_budget)})
              </div>
            </div>
            <button 
              onClick={() => setIsTradeModalOpen(true)}
              className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2.5 rounded-lg font-bold shadow-sm transition-colors"
            >
              Portföyde Al
            </button>
          </div>
        )}

        {/* Content */}
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Sizing Information */}
          {portfolioId && (
            <div className="col-span-full bg-slate-50 p-5 rounded-xl border border-slate-200">
              <h3 className="font-bold text-navy-900 flex items-center gap-2 mb-4">
                <Target size={18} className="text-primary-600" />
                Pozisyon Büyüklüğü ve Risk Sınırları
              </h3>
              
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-4">
                <div>
                  <div className="text-xs text-slate-500 font-medium mb-1">Mevcut Pay</div>
                  <div className="font-bold text-navy-900">{formatPercent(inst.current_position_weight_percentage)}</div>
                  {inst.current_position_quantity != null && inst.current_position_quantity > 0 && (
                    <div className="text-xs text-slate-400">
                      {inst.current_position_quantity} adet ({formatTry(inst.current_position_market_value)})
                    </div>
                  )}
                </div>
                <div>
                  <div className="text-xs text-slate-500 font-medium mb-1">Hedef Pay</div>
                  <div className="font-bold text-navy-900">{formatPercent(inst.recommended_target_weight)}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 font-medium mb-1">Önerilen Sonrası Pay</div>
                  <div className="font-bold text-navy-900">{formatPercent(inst.estimated_post_trade_weight)}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 font-medium mb-1">Tek-Hisse Üst Sınırı</div>
                  <div className="font-bold text-navy-900">{formatPercent(inst.hard_max_weight)}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 font-medium mb-1">Maks. Alınabilir</div>
                  <div className="font-bold text-navy-900">{inst.max_executable_quantity ?? 0} adet</div>
                  <div className="text-xs text-slate-400">{formatTry(inst.max_executable_budget)}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 font-medium mb-1">Risk Durumu</div>
                  <div className={`font-bold ${inst.sizing_state === 'OK' ? 'text-success-600' : 'text-danger-600'}`}>
                    {translateSizingState(inst.sizing_state)}
                  </div>
                </div>
              </div>
              
              <p className="text-xs text-slate-500 italic bg-white p-3 rounded border border-slate-100">
                Bu önerilen tutar; kullanılabilir nakit, toplam portföy değeri, mevcut pozisyon ağırlığı, risk toleransı ve tek-varlık üst sınırı dikkate alınarak hesaplanmıştır.
              </p>
            </div>
          )}

          {/* Scores */}
          <div className="space-y-4">
            <h3 className="font-bold text-navy-900 flex items-center gap-2 border-b border-slate-100 pb-2">
              <Activity size={18} className="text-primary-600" />
              Sistem Puanları
            </h3>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center p-2 hover:bg-slate-50 rounded">
                <span className="text-sm font-medium text-slate-600">Piyasa Görünümü</span>
                <span className={`text-sm font-bold px-2 py-0.5 rounded ${getActionColorClass(inst.market_view, false)}`}>{formatActionLabel(inst.market_view, false)}</span>
              </div>
              
              {portfolioId && inst.personal_action && (
                <div className="flex justify-between items-center p-2 hover:bg-slate-50 rounded">
                  <span className="text-sm font-medium text-slate-600">Kişisel Karar</span>
                  <span className={`text-sm font-bold px-2 py-0.5 rounded ${getActionColorClass(inst.personal_action, false)}`}>{formatActionLabel(inst.personal_action, false)}</span>
                </div>
              )}
              
              <div className="flex justify-between items-center p-2 hover:bg-slate-50 rounded">
                <span className="text-sm font-medium text-slate-600">Piyasa Puanı</span>
                <span className="font-bold text-navy-900">{getScoreDisplay(inst.market_score)}</span>
              </div>
              
              {portfolioId && (
                <div className="flex justify-between items-center p-2 hover:bg-slate-50 rounded">
                  <span className="text-sm font-medium text-slate-600">Kişisel Uyum</span>
                  <span className="font-bold text-primary-600">{getScoreDisplay(inst.personal_score)}</span>
                </div>
              )}
              
              <div className="flex justify-between items-center p-2 hover:bg-slate-50 rounded">
                <span className="text-sm font-medium text-slate-600">Veri Kalitesi</span>
                <span className={`font-bold ${inst.data_quality_score < 50 ? 'text-danger-600' : 'text-navy-900'}`}>
                  {getScoreDisplay(inst.data_quality_score)}
                </span>
              </div>
            </div>
            
            <h3 className="font-bold text-navy-900 flex items-center gap-2 border-b border-slate-100 pb-2 pt-4">
              <TrendingUp size={18} className="text-primary-600" />
              Alt Metrikler
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-2 hover:bg-slate-50 rounded">
                <span className="text-sm font-medium text-slate-600">Teknik Analiz</span>
                <span className="font-bold text-navy-900">{getScoreDisplay(inst.technical_score)}</span>
              </div>
              <div className="flex justify-between items-center p-2 hover:bg-slate-50 rounded">
                <span className="text-sm font-medium text-slate-600">Temel Analiz</span>
                <span className="font-bold text-navy-900">{getScoreDisplay(inst.fundamental_score)}</span>
              </div>
              <div className="flex justify-between items-center p-2 hover:bg-slate-50 rounded">
                <span className="text-sm font-medium text-slate-600">Haber Akışı</span>
                <span className="font-bold text-navy-900">{getScoreDisplay(inst.news_score)}</span>
              </div>
              <div className="flex justify-between items-center p-2 hover:bg-slate-50 rounded">
                <span className="text-sm font-medium text-slate-600">Risk/Getiri</span>
                <span className="font-bold text-navy-900">{getScoreDisplay(inst.risk_reward_score)}</span>
              </div>
            </div>
          </div>

          {/* Reasons and Warnings */}
          <div className="space-y-6">
            <div>
              <h3 className="font-bold text-navy-900 flex items-center gap-2 border-b border-slate-100 pb-2 mb-3">
                <CheckCircle size={18} className="text-success-600" />
                Karar Gerekçeleri
              </h3>
              {inst.reason_codes && inst.reason_codes.length > 0 ? (
                <ul className="space-y-2">
                  {inst.reason_codes.map((rc, i) => (
                    <li key={i} className="flex items-start gap-2 bg-slate-50 p-2.5 rounded text-sm text-slate-700">
                      <div className="w-1.5 h-1.5 rounded-full bg-success-500 mt-1.5 shrink-0"></div>
                      <span>{translateReason(rc)}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-slate-500 italic">Belirgin bir gerekçe sunulmadı.</p>
              )}
            </div>
            
            {portfolioId && inst.sizing_reason_codes && inst.sizing_reason_codes.length > 0 && (
              <div>
                <h3 className="font-bold text-navy-900 flex items-center gap-2 border-b border-slate-100 pb-2 mb-3">
                  <Target size={18} className="text-primary-600" />
                  Pozisyon Büyüklüğü Gerekçeleri
                </h3>
                <ul className="space-y-2">
                  {inst.sizing_reason_codes.map((rc, i) => (
                    <li key={i} className="flex items-start gap-2 bg-primary-50/50 p-2.5 rounded text-sm text-slate-700">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary-500 mt-1.5 shrink-0"></div>
                      <span>{translateSizingReason(rc)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div>
              <h3 className="font-bold text-navy-900 flex items-center gap-2 border-b border-slate-100 pb-2 mb-3">
                <AlertTriangle size={18} className="text-amber-500" />
                Uyarılar
              </h3>
              {inst.warnings && inst.warnings.length > 0 ? (
                <ul className="space-y-2">
                  {inst.warnings.map((warn, i) => (
                    <li key={i} className="flex items-start gap-2 bg-amber-50 p-2.5 rounded text-sm text-amber-800">
                      <div className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0"></div>
                      <span>{translateWarning(warn)}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-slate-500 italic">Önemli bir uyarı bulunmuyor.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {portfolioId && isTradeModalOpen && (
        <PortfolioActionModal
          isOpen={isTradeModalOpen}
          onClose={() => setIsTradeModalOpen(false)}
          portfolioId={portfolioId.toString()}
          initialSymbol={inst.symbol}
          initialQuantity={inst.recommended_quantity || 0}
          initialAction="BUY"
        />
      )}
    </div>
  );
}



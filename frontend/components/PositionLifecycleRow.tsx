import React, { useState } from 'react';
import Link from 'next/link';
import { formatTry, formatQuantity, getProfitLossColorClass } from '@/lib/financialUi';
import { LifecycleHealthState, LifecycleAction, PositionLifecycleDTO } from '@/types/lifecycle';
import { ChevronDown, ChevronUp, AlertCircle, Info, Activity, AlertTriangle } from 'lucide-react';

export interface PortfolioPosition {
  instrument_id: number;
  symbol: string;
  quantity: number | string;
  market_value?: number | string;
  unrealized_pnl?: number | string;
  [key: string]: any;
}

interface PositionLifecycleRowProps {
  pos: PortfolioPosition;
  lc?: PositionLifecycleDTO;
  onOpenActionModal?: (actionType: "DEPOSIT"|"WITHDRAWAL"|"BUY"|"SELL", instrument: { symbol: string; [key: string]: any }, suggestedQuantity?: number) => void;
  isPaper?: boolean;
}

export function translateReasonCode(code: string): string {
  switch (code) {
    case 'PORTFOLIO_CONCENTRATION_BREACH': return 'Portföydeki ağırlık sınırı aşıldı.';
    case 'PARTIAL_REDUCTION_NOT_EXECUTABLE': return 'Pozisyon 1 adet olduğu için kısmi azaltma uygulanabilir değil.';
    case 'MISSING_REQUIRED_DATA': return 'Güvenilir değerlendirme için yeterli güncel veri yok.';
    case 'STALE_DATA': return 'Güvenilir değerlendirme için yeterli güncel veri yok.';
    case 'UNKNOWN_ASSET_CLASS': return 'Varlık sınıfı belirlenemedi.';
    case 'NO_EVALUATION': return 'Henüz değerlendirilmedi.';
    case 'WATCH_DETERIORATION': return 'Piyasa görünümünde bozulma.';
    case 'CONFIRMED_DETERIORATION': return 'Bozulma trendi teyit edildi.';
    case 'EXIT_DETERIORATION': return 'Çıkış şartları sağlandı.';
    case 'STRONG_SELL_EXIT': return 'Güçlü sat sinyali çıkış şartlarını sağladı.';
    case 'NO_ELIGIBLE_OPPORTUNITY': return 'Uygun fırsat bulunamadı.';
    case 'RECOVERING_POSITIVE': return 'Pozitif sinyal alındı.';
    case 'STABLE_POSITIVE': return 'Stabil duruma ulaşıldı.';
    case 'ADD_CONFIRMED': return 'Artırma koşulları sağlandı.';
    default: return 'Ek değerlendirme nedeni mevcut.';
  }
}

export function formatHealthState(state?: string): { label: string; color: string } {
  if (!state) return { label: "Henüz değerlendirilmedi", color: "bg-slate-100 text-slate-800 border-slate-200" };
  if (state === LifecycleHealthState.STABLE) return { label: "Stabil", color: "bg-emerald-100 text-emerald-800 border-emerald-200" };
  if (state === LifecycleHealthState.WATCH) return { label: "İzle", color: "bg-amber-100 text-amber-800 border-amber-200" };
  if (state === LifecycleHealthState.CONFIRMED_DETERIORATION) return { label: "Bozulma doğrulandı", color: "bg-rose-100 text-rose-800 border-rose-200" };
  if (state === LifecycleHealthState.RECOVERING) return { label: "Toparlanıyor", color: "bg-blue-100 text-blue-800 border-blue-200" };
  if (state === LifecycleHealthState.CLOSED) return { label: "Kapalı", color: "bg-slate-100 text-slate-800 border-slate-200" };
  return { label: "Henüz değerlendirilmedi", color: "bg-slate-100 text-slate-800 border-slate-200" };
}

export function formatAction(action?: string): { label: string; color: string } {
  if (!action) return { label: "-", color: "text-slate-400" };
  if (action === LifecycleAction.HOLD) return { label: "Bekle", color: "text-slate-600 font-medium" };
  if (action === LifecycleAction.CONSIDER_ADD) return { label: "Artırmayı değerlendir", color: "text-emerald-600 font-bold" };
  if (action === LifecycleAction.CONSIDER_REDUCE) return { label: "Azaltmayı değerlendir", color: "text-amber-600 font-bold" };
  if (action === LifecycleAction.CONSIDER_EXIT) return { label: "Çıkışı değerlendir", color: "text-rose-600 font-bold" };
  if (action === LifecycleAction.NO_ACTION_DATA) return { label: "Veri yetersiz", color: "text-slate-400 font-medium" };
  return { label: "-", color: "text-slate-400" };
}

export default function PositionLifecycleRow({ pos, lc, onOpenActionModal, isPaper }: PositionLifecycleRowProps) {
  const [expanded, setExpanded] = useState(false);

  const stateInfo = formatHealthState(lc?.health_state);
  const actionInfo = formatAction(lc?.recommended_action);

  const handleActionClick = () => {
    if (!onOpenActionModal) return;
    if (lc?.recommended_action === LifecycleAction.CONSIDER_EXIT || lc?.recommended_action === LifecycleAction.CONSIDER_REDUCE) {
      onOpenActionModal("SELL", pos, lc.suggested_reduce_quantity ? Number(lc.suggested_reduce_quantity) : undefined);
    } else if (lc?.recommended_action === LifecycleAction.CONSIDER_ADD) {
      onOpenActionModal("BUY", pos);
    }
  };

  const isDataInsufficient = lc?.recommended_action === LifecycleAction.NO_ACTION_DATA || lc?.data_state === "MISSING_DATA" || lc?.data_state === "STALE";

  return (
    <>
      <tr className={`hover:bg-slate-50/50 cursor-pointer ${expanded ? 'bg-slate-50' : ''}`} onClick={() => setExpanded(!expanded)} data-testid={`lifecycle-row-${pos.symbol}`}>
        <td className="px-5 py-4 font-semibold text-navy-900 border-l-2 border-transparent">
          <Link href={`/instruments/${pos.symbol}`} className="hover:text-primary-600 hover:underline" onClick={(e) => e.stopPropagation()}>
            {pos.symbol}
          </Link>
        </td>
        <td className="px-5 py-4 text-right font-medium">{formatQuantity(pos.quantity)}</td>
        <td className="px-5 py-4 text-right font-medium hidden md:table-cell">
          {pos.market_value != null ? formatTry(pos.market_value) : 'Yetersiz Veri'}
        </td>
        <td className="px-5 py-4 text-right hidden md:table-cell">
          {pos.unrealized_pnl != null ? (
            <span className={`font-semibold ${getProfitLossColorClass(pos.unrealized_pnl)}`}>
              {Number(pos.unrealized_pnl) > 0 ? '+' : ''}{formatTry(pos.unrealized_pnl)}
            </span>
          ) : (
            <span className="text-slate-500 font-medium">Yetersiz Veri</span>
          )}
        </td>
        <td className="px-5 py-4 text-center">
          <span className={`px-2 py-1 text-[11px] font-semibold rounded-full border ${stateInfo.color}`} data-testid={`lifecycle-health-${pos.symbol}`}>
            {stateInfo.label}
          </span>
        </td>
        <td className="px-5 py-4 text-center">
          <span className={`text-sm ${actionInfo.color}`} data-testid={`lifecycle-action-${pos.symbol}`}>
            {actionInfo.label}
          </span>
        </td>
        <td className="px-5 py-4 text-right text-xs text-slate-500 font-medium hidden md:table-cell">
          {lc?.last_evaluated_at ? new Intl.DateTimeFormat("tr-TR", { hour: "2-digit", minute: "2-digit" }).format(new Date(lc.last_evaluated_at)) : "-"}
        </td>
        <td className="px-5 py-4 text-center text-slate-400">
          {expanded ? <ChevronUp className="w-5 h-5 mx-auto" /> : <ChevronDown className="w-5 h-5 mx-auto" />}
        </td>
      </tr>
      
      {expanded && (
        <tr className="bg-slate-50/80 border-b border-slate-100" data-testid={`lifecycle-details-${pos.symbol}`}>
          <td colSpan={8} className="p-0">
            <div className="px-6 py-4 border-l-2 border-primary-400">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Details Section */}
                <div className="space-y-3">
                  <h4 className="text-sm font-bold text-navy-900 flex items-center gap-2">
                    <Activity className="w-4 h-4 text-slate-500" />
                    Karar Özeti
                  </h4>
                  
                  {isDataInsufficient ? (
                    <div className="bg-slate-100 p-3 rounded-md border border-slate-200">
                      <p className="text-sm text-slate-600 flex items-start gap-2">
                        <AlertCircle className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
                        Güvenilir bir değerlendirme için yeterli veri sağlanamadı. Güvenilmez eylemler üretilmeyecektir.
                      </p>
                    </div>
                  ) : !lc ? (
                    <div className="bg-slate-100 p-3 rounded-md border border-slate-200">
                      <p className="text-sm text-slate-600">Henüz değerlendirilmedi.</p>
                    </div>
                  ) : (
                    <>
                      {lc.health_state === LifecycleHealthState.WATCH && (
                        <p className="text-sm text-amber-700 bg-amber-50 p-2 rounded border border-amber-100">
                          İlk olumsuz gözlem kaydedildi. Henüz doğrulanmış bozulma yok.
                        </p>
                      )}
                      
                      {lc.health_state === LifecycleHealthState.RECOVERING && (
                        <p className="text-sm text-blue-700 bg-blue-50 p-2 rounded border border-blue-100">
                          Bozulma sonrası ilk olumlu doğrulama alındı. Stabil duruma dönmek için bir olumlu gözlem daha gerekiyor.
                        </p>
                      )}

                      {lc.recommended_action === LifecycleAction.CONSIDER_REDUCE && lc.suggested_reduce_quantity === 0 && (
                        <p className="text-sm text-rose-700 bg-rose-50 p-2 rounded border border-rose-100 flex items-start gap-2">
                           <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                           Pozisyon 1 adet olduğu için kısmi azaltma uygulanabilir değil.
                        </p>
                      )}

                      <div className="text-sm text-slate-600 space-y-1 mt-2">
                        {lc.evidence?.market_view && (
                          <div className="flex justify-between">
                            <span className="text-slate-500">Piyasa Görünümü:</span>
                            <span className="font-medium text-navy-900">{lc.evidence.market_view}</span>
                          </div>
                        )}
                        <div className="flex justify-between">
                          <span className="text-slate-500">Bölüm (Episode):</span>
                          <span className="font-medium text-navy-900">{lc.episode_number}</span>
                        </div>
                        {Number(lc.negative_confirmation_count) > 0 && (
                           <div className="flex justify-between">
                             <span className="text-slate-500">Negatif Onay:</span>
                             <span className="font-medium text-rose-600">{lc.negative_confirmation_count}</span>
                           </div>
                        )}
                        {Number(lc.recovery_confirmation_count) > 0 && (
                           <div className="flex justify-between">
                             <span className="text-slate-500">Pozitif Onay:</span>
                             <span className="font-medium text-blue-600">{lc.recovery_confirmation_count}</span>
                           </div>
                        )}
                      </div>
                    </>
                  )}
                </div>

                {/* Evidence/Reasons Section */}
                {lc?.evidence?.reason_codes && lc.evidence.reason_codes.length > 0 && (
                  <div className="space-y-3">
                    <h4 className="text-sm font-bold text-navy-900 flex items-center gap-2">
                      <Info className="w-4 h-4 text-slate-500" />
                      Nedenler
                    </h4>
                    <ul className="space-y-2">
                      {lc.evidence.reason_codes.map(code => (
                        <li key={code} className="text-sm text-slate-600 bg-white p-2 rounded border border-slate-200">
                          {translateReasonCode(code)}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Sizing/Transaction Preview Section */}
                {lc && [LifecycleAction.CONSIDER_REDUCE, LifecycleAction.CONSIDER_EXIT].includes(lc.recommended_action) && !isDataInsufficient && Number(lc.suggested_reduce_quantity) > 0 && (
                  <div className="space-y-3">
                    <h4 className="text-sm font-bold text-navy-900 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-slate-500" />
                      Eylem Detayı
                    </h4>
                    <div className="bg-white p-3 rounded-md border border-slate-200 space-y-2">
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-slate-500">Önerilen Satış Adedi:</span>
                        <span className="font-bold text-navy-900">{formatQuantity(lc.suggested_reduce_quantity)}</span>
                      </div>
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-slate-500">Kalan Adet:</span>
                        <span className="font-medium text-navy-900">{formatQuantity(lc.suggested_remaining_quantity)}</span>
                      </div>
                      <div className="flex justify-between items-center text-sm border-t border-slate-100 pt-2 mt-2">
                        <span className="text-slate-500 font-medium">Tahmini Serbest Kalacak Nakit:</span>
                        <span className="font-bold text-emerald-600">{formatTry(lc.estimated_released_cash_base)}</span>
                      </div>
                      <div className="text-[10px] text-slate-400 text-right uppercase tracking-wider font-semibold">TAHMİN / ÖNİZLEME</div>
                    </div>

                    {!isPaper ? (
                      <p className="text-xs text-slate-500 mb-2">
                        Öneri otomatik uygulanmaz. Satışı dışarıda yaptıktan sonra kaydedin.
                      </p>
                    ) : (
                      <p className="text-xs text-slate-500 mb-2">
                        Öneri otomatik uygulanmaz. Uygulamak için işlemi onaylayın.
                      </p>
                    )}

                    <button 
                      onClick={(e) => { e.stopPropagation(); handleActionClick(); }}
                      data-testid={`lifecycle-sell-${pos.symbol}`}
                      className="w-full bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 py-2 rounded text-sm font-bold transition-colors"
                    >
                      {isPaper ? "Satışı Simüle Et" : "Satışı Kaydet"}
                    </button>
                  </div>
                )}
                
                {lc && lc.recommended_action === LifecycleAction.CONSIDER_ADD && !isDataInsufficient && (
                  <div className="space-y-3">
                    <h4 className="text-sm font-bold text-navy-900 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-slate-500" />
                      Eylem Detayı
                    </h4>
                    
                    <p className="text-xs text-slate-500 mb-2">
                      Bu işlem için portföydeki nakit kullanılacaktır.
                    </p>

                    <button 
                      onClick={(e) => { e.stopPropagation(); handleActionClick(); }}
                      data-testid={`lifecycle-buy-${pos.symbol}`}
                      className="w-full bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 py-2 rounded text-sm font-bold transition-colors"
                    >
                      {isPaper ? "Alımı Simüle Et" : "Alımı Kaydet"}
                    </button>
                  </div>
                )}
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

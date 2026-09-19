'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchApi } from '@/lib/api';
import { BasketPreviewResponse, BasketItemDTO } from '@/lib/types';
import { formatMoney, formatTry, formatPercent } from '@/lib/financialUi';
import { RefreshCw, Calculator, Loader2, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';
import { DataStateBadge } from './DataStateBadge';

interface BasketBuilderProps {
  portfolioId: number;
}

export function BasketBuilder({ portfolioId }: BasketBuilderProps) {
  const queryClient = useQueryClient();
  const [amount, setAmount] = useState<string>('');
  const [manualPrices, setManualPrices] = useState<Record<number, string>>({});

  const { data: preview, isLoading, error, refetch } = useQuery<BasketPreviewResponse>({
    queryKey: ['basket-preview', portfolioId, amount, manualPrices],
    queryFn: async () => {
      const payload: any = {};
      if (amount && !isNaN(Number(amount))) {
        payload.deploy_amount = Number(amount);
      }

      return fetchApi(`/api/v1/portfolios/${portfolioId}/basket-preview`, {
        method: 'POST',
        body: JSON.stringify(payload)
      });
    },
    // Only automatically refetch if the amount is a valid number or empty
    enabled: !!portfolioId && (amount === '' || !isNaN(Number(amount))),
    retry: false
  });

  const handlePriceChange = (instrumentId: number, value: string) => {
    setManualPrices(prev => ({
      ...prev,
      [instrumentId]: value
    }));
  };

  const updateExecutionPreview = async (instrumentId: number) => {
    const priceStr = manualPrices[instrumentId];
    if (!priceStr || isNaN(Number(priceStr))) return;
    
    try {
      const res = (await fetchApi(`/api/v1/portfolios/${portfolioId}/execution-preview`, {
        method: 'POST',
        body: JSON.stringify({
          instrument_id: instrumentId,
          manual_native_price: Number(priceStr)
        })
      })) as any;
      alert(`İşlem Önizlemesi Alındı:\nAdet: ${res.recomputed_quantity}\nBütçe: ${res.recomputed_budget}`);
    } catch (err: any) {
      alert("Hata: " + err.message);
    }
  };

  if (isLoading && !preview) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader2 className="w-8 h-8 text-primary-500 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-700 p-4 rounded-lg flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 mt-0.5 shrink-0" />
        <div>
          <h4 className="font-semibold">Sepet oluşturulurken hata oluştu</h4>
          <p className="text-sm mt-1">{(error as any).message || 'Bilinmeyen bir hata.'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
        <div className="flex flex-col sm:flex-row gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Yatırılacak Tutar (İsteğe Bağlı)
            </label>
            <div className="relative">
              <input
                type="number"
                placeholder="Örn: 10000"
                className="w-full bg-slate-50 border border-slate-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:outline-none"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
              />
              <span className="absolute right-3 top-2.5 text-slate-400 font-medium">{preview?.base_currency || 'TRY'}</span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Boş bırakılırsa portföydeki serbest nakit ({formatMoney(preview?.available_cash, preview?.base_currency)}) kullanılır.
            </p>
          </div>
          <button 
            onClick={() => refetch()}
            className="px-6 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg font-bold shadow-sm transition-colors flex items-center gap-2"
          >
            <Calculator size={18} />
            Sepeti Hesapla
          </button>
        </div>
      </div>

      {preview && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
              <div className="text-sm text-slate-500 font-medium">Hedef Nakit</div>
              <div className="text-xl font-bold text-navy-900 mt-1">{formatMoney(preview.target_cash_reserve, preview.base_currency)}</div>
            </div>
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
              <div className="text-sm text-slate-500 font-medium">Dağıtılan Tutar</div>
              <div className="text-xl font-bold text-emerald-600 mt-1">{formatMoney(preview.allocated_amount, preview.base_currency)}</div>
            </div>
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
              <div className="text-sm text-slate-500 font-medium">Dağıtılamayan Tutar</div>
              <div className="text-xl font-bold text-amber-600 mt-1">{formatMoney(preview.unallocated_amount, preview.base_currency)}</div>
            </div>
            <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
              <div className="text-sm text-slate-500 font-medium">Veri Durumu</div>
              <div className="mt-1">
                <DataStateBadge state={preview.data_state} />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
              <h3 className="font-bold text-navy-900">Varlık Sınıfı Hedefleri</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead className="bg-slate-50 text-slate-600 text-sm">
                  <tr>
                    <th className="px-5 py-3 font-medium">Varlık Sınıfı</th>
                    <th className="px-5 py-3 font-medium text-right">Mevcut Değer</th>
                    <th className="px-5 py-3 font-medium text-right">Mevcut Ağırlık</th>
                    <th className="px-5 py-3 font-medium text-right">Hedef Ağırlık</th>
                    <th className="px-5 py-3 font-medium text-right">Önerilen Değer</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-sm">
                  {preview.sleeves.map(sleeve => (
                    <tr key={sleeve.asset_class}>
                      <td className="px-5 py-3 font-semibold text-navy-800">{sleeve.asset_class.replace('_', ' ')}</td>
                      <td className="px-5 py-3 text-right">{formatMoney(sleeve.current_value, preview.base_currency)}</td>
                      <td className="px-5 py-3 text-right">{formatPercent(sleeve.current_weight)}</td>
                      <td className="px-5 py-3 text-right">{formatPercent(sleeve.target_weight)}</td>
                      <td className="px-5 py-3 text-right font-medium text-emerald-600">{formatMoney(sleeve.proposed_allocation, preview.base_currency)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-100 bg-slate-50">
              <h3 className="font-bold text-navy-900">Sepet Bileşenleri</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead className="bg-slate-50 text-slate-600 text-xs uppercase tracking-wider">
                  <tr>
                    <th className="px-5 py-3 font-medium">Sembol</th>
                    <th className="px-5 py-3 font-medium">Karar</th>
                    <th className="px-5 py-3 font-medium text-right">Native Fiyat</th>
                    <th className="px-5 py-3 font-medium text-right">Kabul Edilen Fiyat</th>
                    <th className="px-5 py-3 font-medium text-right">Adet</th>
                    <th className="px-5 py-3 font-medium text-right">Bütçe ({preview.base_currency})</th>
                    <th className="px-5 py-3 font-medium">Neden Kodları</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-sm">
                  {preview.items.map(item => (
                    <tr key={item.symbol} className={item.proposed_quantity > 0 ? "bg-emerald-50/30" : ""}>
                      <td className="px-5 py-3">
                        <div className="font-bold text-navy-900">{item.symbol}</div>
                        <div className="text-xs text-slate-500">{item.asset_class.replace('_', ' ')}</div>
                      </td>
                      <td className="px-5 py-3">
                        <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                          item.personal_action === 'BUY' || item.personal_action === 'STRONG_BUY' 
                            ? 'bg-emerald-100 text-emerald-800' 
                            : 'bg-slate-100 text-slate-800'
                        }`}>
                          {item.personal_action}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-right font-medium">
                        {formatMoney(item.analysis_native_price, item.native_currency)}
                      </td>
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-2">
                          <input
                            type="number"
                            step="0.01"
                            placeholder={item.analysis_native_price.toString()}
                            value={manualPrices[item.instrument_id] ?? ''}
                            onChange={(e) => handlePriceChange(item.instrument_id, e.target.value)}
                            className="w-24 text-right border border-slate-300 rounded px-2 py-1 text-sm focus:ring-1 focus:ring-primary-500 focus:outline-none"
                          />
                          <button
                            onClick={() => updateExecutionPreview(item.instrument_id)}
                            className="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs rounded"
                          >
                            Önizle
                          </button>
                        </div>
                      </td>
                      <td className="px-5 py-3 text-right font-bold text-navy-900">
                        {item.proposed_quantity}
                      </td>
                      <td className="px-5 py-3 text-right text-emerald-600 font-medium">
                        {formatMoney(item.proposed_base_budget, preview.base_currency)}
                      </td>
                      <td className="px-5 py-3">
                        <div className="flex flex-wrap gap-1">
                          {item.reason_codes.map(code => (
                            <span key={code} className="px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded text-[10px]" title={code}>
                              {code.split('_').pop()}
                            </span>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                  {preview.items.length === 0 && (
                    <tr>
                      <td colSpan={7} className="px-5 py-8 text-center text-slate-500">
                        Sepete eklenecek uygun varlık bulunamadı.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

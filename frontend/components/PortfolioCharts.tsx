"use client";

import { useQuery } from "@tanstack/react-query";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, Legend } from "recharts";
import { fetchApi } from "@/lib/api";
import { Clock } from "lucide-react";
import { formatTry, formatPercent, formatQuantity, colorForSymbol, CASH_COLOR } from "@/lib/financialUi";

export function PortfolioCharts({ portfolioId, summary }: { portfolioId: string, summary: any }) {
  const { data: transactions, isLoading: isTxsLoading } = useQuery<any[]>({
    queryKey: ["portfolio", portfolioId, "transactions"],
    queryFn: () => fetchApi(`/api/v1/portfolios/${portfolioId}/transactions`),
  });

  // Prepare data for donut chart
  const allocationData = summary?.positions
    ?.filter((p: any) => p.market_value && p.market_value > 0)
    .map((p: any) => ({
      name: p.symbol,
      value: Number(p.market_value),
      quantity: Number(p.quantity),
      isCash: false
    })) || [];

  if (summary?.cash_balance > 0) {
    allocationData.push({
      name: "Nakit",
      value: Number(summary.cash_balance),
      quantity: Number(summary.cash_balance),
      isCash: true
    });
  }

  // Calculate Total
  const hasPartialData = summary?.positions?.some((p: any) => p.market_value === null || p.market_value === undefined);
  const totalValue = allocationData.reduce((acc: number, curr: any) => acc + curr.value, 0);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const percentage = totalValue > 0 ? (data.value / totalValue) * 100 : 0;
      
      return (
        <div className="bg-white p-3 border border-slate-200 shadow-md rounded-lg text-sm">
          <p className="font-bold text-navy-900 mb-1">{data.name}</p>
          {data.isCash ? (
            <p className="text-slate-600">Tutar: <span className="font-medium text-navy-900">{formatTry(data.value)}</span></p>
          ) : (
            <>
              <p className="text-slate-600">Piyasa Değeri: <span className="font-medium text-navy-900">{formatTry(data.value)}</span></p>
              <p className="text-slate-600">Adet: <span className="font-medium text-navy-900">{formatQuantity(data.quantity)}</span></p>
            </>
          )}
          <p className="text-slate-600">Portföy Payı: <span className="font-medium text-navy-900">{formatPercent(percentage)}</span></p>
        </div>
      );
    }
    return null;
  };

  const CustomLegend = ({ payload }: any) => {
    return (
      <div className="flex flex-col gap-2 max-h-32 overflow-y-auto px-2">
        {payload.map((entry: any, index: number) => {
          const data = allocationData.find((d: any) => d.name === entry.value);
          const percentage = data && totalValue > 0 ? (data.value / totalValue) * 100 : 0;
          return (
            <div key={`item-${index}`} className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }} />
                <span className="font-medium text-navy-900 truncate max-w-[80px]" title={entry.value}>{entry.value}</span>
              </div>
              <div className="flex items-center gap-3 text-right">
                <span className="text-slate-600 w-20">{data ? formatTry(data.value) : '-'}</span>
                <span className="font-medium text-slate-700 w-12">{formatPercent(percentage)}</span>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
      {/* Allocation Donut Chart */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 lg:col-span-1 flex flex-col">
        <h2 className="text-lg font-bold text-navy-900 mb-4">Varlık Dağılımı</h2>
        <div className="flex-1 min-h-[300px]">
          {allocationData.length === 0 ? (
            <div className="h-full flex items-center justify-center text-slate-400 text-sm">
              Portföy dağılımı için henüz pozisyon bulunmuyor.
            </div>
          ) : (
            <div className="relative w-full h-full min-h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={allocationData}
                    cx="50%"
                    cy="40%"
                    innerRadius={70}
                    outerRadius={95}

                  paddingAngle={2}
                  dataKey="value"
                  stroke="#fff"
                  strokeWidth={2}
                >
                  {allocationData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={colorForSymbol(entry.name)} />
                  ))}
                </Pie>
                <RechartsTooltip content={<CustomTooltip />} />
                <Legend content={<CustomLegend />} verticalAlign="bottom" />
                
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute top-[40%] left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center justify-center pointer-events-none text-center w-[130px]">
                <span className="text-[11px] text-slate-500 font-medium uppercase tracking-wide">
                  {hasPartialData ? "Kısmi Veri" : "Toplam Değer"}
                </span>
                <span className="text-sm font-bold text-navy-900 leading-tight">
                  {hasPartialData ? "-" : formatTry(totalValue)}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Transaction History */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 lg:col-span-2 flex flex-col">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-bold text-navy-900">İşlem Geçmişi</h2>
        </div>
        <div className="flex-1 overflow-auto max-h-[350px]">
          {isTxsLoading ? (
            <div className="text-slate-400 text-sm p-4 text-center">Yükleniyor...</div>
          ) : !transactions || transactions.length === 0 ? (
            <div className="text-slate-400 text-sm p-4 text-center h-full flex items-center justify-center">
              Henüz işlem yapılmamış.
            </div>
          ) : (
            <>
              {/* Desktop Table */}
              <table className="w-full text-left text-sm hidden md:table">
                <thead className="bg-slate-50 text-slate-600 sticky top-0">
                  <tr>
                    <th className="px-4 py-2 font-medium">Tarih</th>
                    <th className="px-4 py-2 font-medium">Tür</th>
                    <th className="px-4 py-2 font-medium">Varlık</th>
                    <th className="px-4 py-2 font-medium text-right">Adet / Tutar</th>
                    <th className="px-4 py-2 font-medium text-right">Fiyat</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {transactions.map((tx: any) => {
                    const isCash = tx.transaction_type === 'DEPOSIT' || tx.transaction_type === 'WITHDRAWAL';
                    return (
                      <tr key={tx.id} className="hover:bg-slate-50/50">
                        <td className="px-4 py-3 text-slate-500 flex items-center gap-1">
                          <Clock size={14} />
                          {new Date(tx.executed_at).toLocaleString('tr-TR', { dateStyle: 'short', timeStyle: 'short' })}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`text-xs font-bold px-2 py-1 rounded ${
                            tx.transaction_type === 'BUY' ? 'bg-blue-100 text-blue-700' :
                            tx.transaction_type === 'SELL' ? 'bg-amber-100 text-amber-700' :
                            tx.transaction_type === 'DEPOSIT' ? 'bg-emerald-100 text-emerald-700' :
                            'bg-rose-100 text-rose-700'
                          }`}>
                            {tx.transaction_type === 'BUY' ? 'AL' :
                             tx.transaction_type === 'SELL' ? 'SAT' :
                             tx.transaction_type === 'DEPOSIT' ? 'YATIRMA' : 'ÇEKİM'}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-medium text-navy-900">
                          {tx.instrument_symbol || 'Nakit'}
                        </td>
                        <td className="px-4 py-3 text-right font-medium">
                          {isCash ? formatTry(tx.quantity) : formatQuantity(tx.quantity)}
                        </td>
                        <td className="px-4 py-3 text-right text-slate-600">
                          {!isCash && tx.price ? formatTry(tx.price) : '-'}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
              
              {/* Mobile Cards */}
              <div className="flex flex-col gap-3 md:hidden">
                {transactions.map((tx: any) => {
                  const isCash = tx.transaction_type === 'DEPOSIT' || tx.transaction_type === 'WITHDRAWAL';
                  return (
                    <div key={tx.id} className="bg-slate-50 p-3 rounded-lg border border-slate-100 flex flex-col gap-2">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center gap-2">
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                            tx.transaction_type === 'BUY' ? 'bg-blue-100 text-blue-700' :
                            tx.transaction_type === 'SELL' ? 'bg-amber-100 text-amber-700' :
                            tx.transaction_type === 'DEPOSIT' ? 'bg-emerald-100 text-emerald-700' :
                            'bg-rose-100 text-rose-700'
                          }`}>
                            {tx.transaction_type === 'BUY' ? 'AL' :
                             tx.transaction_type === 'SELL' ? 'SAT' :
                             tx.transaction_type === 'DEPOSIT' ? 'YATIRMA' : 'ÇEKİM'}
                          </span>
                          <span className="font-bold text-navy-900 text-sm">{tx.instrument_symbol || 'Nakit'}</span>
                        </div>
                        <div className="text-xs text-slate-500 flex items-center gap-1">
                          <Clock size={12} />
                          {new Date(tx.executed_at).toLocaleString('tr-TR', { dateStyle: 'short', timeStyle: 'short' })}
                        </div>
                      </div>
                      <div className="flex justify-between items-end text-sm">
                        <div className="flex flex-col">
                          <span className="text-slate-500 text-xs">Adet / Tutar</span>
                          <span className="font-medium text-navy-900">{isCash ? formatTry(tx.quantity) : formatQuantity(tx.quantity)}</span>
                        </div>
                        <div className="flex flex-col items-end">
                          <span className="text-slate-500 text-xs">Fiyat</span>
                          <span className="font-medium text-slate-700">{!isCash && tx.price ? formatTry(tx.price) : '-'}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

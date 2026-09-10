"use client";

import { useQuery } from "@tanstack/react-query";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { fetchApi } from "@/lib/api";
import { Clock } from "lucide-react";

const COLORS = ['#0284c7', '#0369a1', '#0ea5e9', '#38bdf8', '#7dd3fc', '#bae6fd'];

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
      value: Number(p.market_value)
    })) || [];

  if (summary?.cash_balance > 0) {
    allocationData.push({
      name: "Nakit",
      value: Number(summary.cash_balance)
    });
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
      {/* Allocation Donut Chart */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 lg:col-span-1 flex flex-col">
        <h2 className="text-lg font-bold text-navy-900 mb-4">Varlık Dağılımı</h2>
        <div className="flex-1 min-h-[300px]">
          {allocationData.length === 0 ? (
            <div className="h-full flex items-center justify-center text-slate-400 text-sm">
              Veri yok
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {allocationData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: any) => `${Number(value).toLocaleString('tr-TR', { maximumFractionDigits: 0 })} ₺`}
                />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
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
            <table className="w-full text-left text-sm">
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
                  const isCash = tx.transaction_type === 'DEPOSIT' || tx.transaction_type === 'WITHDRAW';
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
                           tx.transaction_type === 'DEPOSIT' ? 'YATIRMA' : 'ÇEKME'}
                        </span>
                      </td>
                      <td className="px-4 py-3 font-medium text-navy-900">
                        {tx.instrument_symbol || 'Nakit'}
                      </td>
                      <td className="px-4 py-3 text-right font-medium">
                        {isCash ? `${Number(tx.quantity).toLocaleString('tr-TR')} ₺` : Number(tx.quantity).toLocaleString('tr-TR')}
                      </td>
                      <td className="px-4 py-3 text-right text-slate-600">
                        {!isCash && tx.price ? `${Number(tx.price).toLocaleString('tr-TR')} ₺` : '-'}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

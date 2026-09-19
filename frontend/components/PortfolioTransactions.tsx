"use client";
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api";
import { formatTry, formatQuantity } from "@/lib/financialUi";
import { Activity } from "lucide-react";

export function PortfolioTransactions({ portfolioId }: { portfolioId: string }) {
  const { data: txs, isLoading, isError } = useQuery<any[]>({
    queryKey: ["portfolio", portfolioId, "transactions"],
    queryFn: () => fetchApi(`/api/v1/portfolios/${portfolioId}/transactions`),
  });

  if (isLoading) return <div className="p-6 text-slate-500">İşlemler yükleniyor...</div>;
  if (isError) return <div className="p-6 text-red-500">İşlemler alınamadı.</div>;

  if (!txs || txs.length === 0) {
    return (
      <div className="p-12 text-center text-slate-500 flex flex-col items-center">
        <Activity className="w-12 h-12 text-slate-300 mb-3" />
        <p className="font-medium text-navy-900 mb-1">Henüz İşlem Yok</p>
        <p className="text-sm">Bu portföyde henüz bir işlem gerçekleştirilmedi.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm min-w-[700px]">
        <thead className="bg-slate-50 text-slate-600 font-medium">
          <tr>
            <th className="px-5 py-3">Tarih</th>
            <th className="px-5 py-3">Tür</th>
            <th className="px-5 py-3">Sembol</th>
            <th className="px-5 py-3 text-right">Fiyat</th>
            <th className="px-5 py-3 text-right">Adet</th>
            <th className="px-5 py-3 text-right">Tutar</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {txs.map((t: any) => (
            <tr key={t.id} className="hover:bg-slate-50/50">
              <td className="px-5 py-4 text-slate-600">
                {new Date(t.transaction_date).toLocaleString("tr-TR", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })}
              </td>
              <td className="px-5 py-4">
                <span className={`px-2 py-0.5 text-xs font-semibold rounded ${
                  t.transaction_type === "DEPOSIT" ? "bg-emerald-100 text-emerald-700" :
                  t.transaction_type === "WITHDRAWAL" ? "bg-rose-100 text-rose-700" :
                  t.transaction_type === "BUY" ? "bg-primary-100 text-primary-700" :
                  "bg-purple-100 text-purple-700"
                }`}>
                  {t.transaction_type === "BUY" ? "AL" : 
                   t.transaction_type === "SELL" ? "SAT" : 
                   t.transaction_type === "DEPOSIT" ? "YATIRMA" : "ÇEKİM"}
                </span>
              </td>
              <td className="px-5 py-4 font-semibold text-navy-900">{t.symbol || "-"}</td>
              <td className="px-5 py-4 text-right font-medium">
                {t.price != null ? formatTry(t.price) : "-"}
              </td>
              <td className="px-5 py-4 text-right font-medium">
                {t.quantity != null ? formatQuantity(t.quantity) : "-"}
              </td>
              <td className="px-5 py-4 text-right font-semibold text-navy-900">
                {t.total_amount != null ? formatTry(t.total_amount) : "-"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

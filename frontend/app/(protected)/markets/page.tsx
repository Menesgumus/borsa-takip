"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetchApi } from "@/lib/api";
import { DataStateBadge } from "@/components/DataStateBadge";
import { Search, ChevronRight, RefreshCw, AlertCircle } from "lucide-react";
import { useState } from "react";

const PAGE_SIZE = 20;

interface BatchQuoteItem {
  symbol: string;
  status: "AVAILABLE" | "UNAVAILABLE" | "PROVIDER_ERROR" | "TIMEOUT" | "NOT_FOUND";
  quote?: {
    symbol: string;
    price: string;
    change_pct: string;
    previous_close: string;
    data_state: string;
  };
  error_code?: string;
}

interface BatchQuoteResponse {
  items: Record<string, BatchQuoteItem>;
  requested_count: number;
  available_count: number;
  unavailable_count: number;
  as_of: string;
}

function QuotePriceCell({ item }: { item: BatchQuoteItem | undefined }) {
  if (!item || item.status === "NOT_FOUND" || item.status === "UNAVAILABLE") {
    return <td className="px-6 py-3 text-right text-slate-400 text-sm">—</td>;
  }
  if (item.status === "PROVIDER_ERROR" || item.status === "TIMEOUT") {
    return (
      <td className="px-6 py-3 text-right">
        <span className="text-xs text-amber-600 flex items-center justify-end gap-1">
          <AlertCircle size={11} /> Gecikmeli
        </span>
      </td>
    );
  }
  if (item.status === "AVAILABLE" && item.quote) {
    return (
      <td className="px-6 py-3 text-right font-medium text-navy-900">
        {Number(item.quote.price).toFixed(2)} ₺
      </td>
    );
  }
  return <td className="px-6 py-3 text-right text-slate-400 text-sm">—</td>;
}

function QuoteChangeCell({ item }: { item: BatchQuoteItem | undefined }) {
  if (!item || item.status !== "AVAILABLE" || !item.quote) {
    return <td className="px-6 py-3 text-right text-slate-400 text-sm">—</td>;
  }
  const pct = Number(item.quote.change_pct);
  const change = (Number(item.quote.price) - Number(item.quote.previous_close)).toFixed(2);
  const isPos = pct >= 0;
  return (
    <td className={`px-6 py-3 text-right font-medium text-sm ${isPos ? "text-success-600" : "text-danger-600"}`}>
      {isPos ? "+" : ""}{change} ({isPos ? "+" : ""}{pct.toFixed(2)}%)
    </td>
  );
}

function MarketsTable() {
  const [searchTerm, setSearchTerm] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["instruments", "list", page],
    queryFn: () => fetchApi(`/api/v1/instruments?page=${page}&size=${PAGE_SIZE}`),
    staleTime: 60_000,
    retry: (failureCount: number, err: any) => {
      if (err?.status >= 400 && err?.status < 500) return false;
      return failureCount < 1;
    },
  });

  const instruments: any[] = (data as any)?.items ?? [];
  const total: number = (data as any)?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const filtered = searchTerm
    ? instruments.filter(
        (inst) =>
          inst.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (inst.name && inst.name.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    : instruments;

  const symbolsParam = filtered.map((i) => i.symbol).join(",");

  const {
    data: quotesData,
    isError: isQuotesError,
    isLoading: isQuotesLoading,
    refetch: refetchQuotes,
  } = useQuery<BatchQuoteResponse>({
    queryKey: ["quotes_batch", symbolsParam],
    queryFn: () =>
      symbolsParam
        ? fetchApi(`/api/v1/instruments/quotes/batch?symbols=${symbolsParam}`)
        : Promise.resolve({ items: {}, requested_count: 0, available_count: 0, unavailable_count: 0, as_of: "" }),
    enabled: !!symbolsParam && !isLoading && !isError,
    refetchInterval: 30_000,
    staleTime: 25_000,
    retry: false,
  });

  return (
    <div className="bg-surface rounded-xl border border-navy-800/10 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-navy-800/10 flex flex-col sm:flex-row gap-4 justify-between items-center bg-slate-50">
        <div className="relative w-full sm:w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            placeholder="Sembol veya şirket ara..."
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setPage(1);
            }}
            className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="flex gap-2 overflow-x-auto pb-2 sm:pb-0">
            <button className="px-3 py-1.5 bg-navy-900 text-white text-sm font-medium rounded-md whitespace-nowrap">
              BIST 100
            </button>
            <button className="px-3 py-1.5 bg-white border border-slate-200 text-navy-700 text-sm font-medium rounded-md whitespace-nowrap opacity-50 cursor-not-allowed">
              FX
            </button>
            <button className="px-3 py-1.5 bg-white border border-slate-200 text-navy-700 text-sm font-medium rounded-md whitespace-nowrap opacity-50 cursor-not-allowed">
              Kripto
            </button>
          </div>
          {isQuotesError && (
            <button
              onClick={() => refetchQuotes()}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-amber-700 bg-amber-50 border border-amber-200 rounded-md hover:bg-amber-100 transition-colors whitespace-nowrap"
            >
              <RefreshCw size={14} /> Fiyatları Yenile
            </button>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white border-b border-navy-800/10 text-xs uppercase text-navy-700/60 font-semibold">
              <th className="px-6 py-4">Sembol</th>
              <th className="px-6 py-4 hidden md:table-cell">Şirket</th>
              <th className="px-6 py-4 text-right">Fiyat</th>
              <th className="px-6 py-4 text-right">Değişim</th>
              <th className="px-6 py-4 hidden sm:table-cell">Tür</th>
              <th className="px-6 py-4"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {isError ? (
              <tr>
                <td colSpan={6} className="p-10 text-center">
                  <div className="flex flex-col items-center gap-3">
                    <AlertCircle className="text-danger-500" size={28} />
                    <p className="font-semibold text-danger-700">Veri yüklenirken hata oluştu</p>
                    <p className="text-sm text-slate-500">Oturumunuzu kontrol edin veya daha sonra tekrar deneyin.</p>
                    <button
                      onClick={() => refetch()}
                      className="px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
                    >
                      Tekrar Dene
                    </button>
                  </div>
                </td>
              </tr>
            ) : isLoading ? (
              Array.from({ length: PAGE_SIZE }).map((_, i) => (
                <tr key={i} className="animate-pulse">
                  <td className="px-6 py-4"><div className="h-4 w-16 bg-slate-100 rounded" /></td>
                  <td className="px-6 py-4 hidden md:table-cell"><div className="h-4 w-40 bg-slate-100 rounded" /></td>
                  <td className="px-6 py-4"><div className="h-4 w-16 bg-slate-100 rounded ml-auto" /></td>
                  <td className="px-6 py-4"><div className="h-4 w-20 bg-slate-100 rounded ml-auto" /></td>
                  <td className="px-6 py-4 hidden sm:table-cell"><div className="h-4 w-10 bg-slate-100 rounded" /></td>
                  <td className="px-6 py-4"></td>
                </tr>
              ))
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={6} className="p-8 text-center text-slate-500">
                  {searchTerm ? `"${searchTerm}" için sonuç bulunamadı.` : "Enstrüman bulunamadı."}
                </td>
              </tr>
            ) : (
              filtered.map((inst) => {
                const item = quotesData?.items?.[inst.symbol];
                const q = item?.quote;
                const dataState = q?.data_state;
                return (
                  <tr key={inst.symbol} className="hover:bg-slate-50 group transition-colors">
                    <td className="px-6 py-3 font-bold text-navy-900">
                      <Link href={`/instruments/${inst.symbol}`} className="hover:text-primary-600 flex items-center gap-2">
                        {inst.symbol}
                        {isQuotesLoading && (
                          <span className="inline-block h-3 w-8 bg-slate-100 rounded animate-pulse" />
                        )}
                        {!isQuotesLoading && dataState && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded-sm bg-slate-100 text-slate-500 font-medium">
                            {dataState === "DELAYED" ? "Gecikmeli" : dataState === "EOD" ? "Gün Sonu" : dataState}
                          </span>
                        )}
                      </Link>
                    </td>
                    <td className="px-6 py-3 text-sm text-navy-700/80 hidden md:table-cell max-w-[220px] truncate">
                      {inst.name && inst.name !== inst.symbol ? inst.name : "—"}
                    </td>
                    <QuotePriceCell item={isQuotesLoading ? undefined : item} />
                    <QuoteChangeCell item={isQuotesLoading ? undefined : item} />
                    <td className="px-6 py-3 text-sm text-slate-500 hidden sm:table-cell">Hisse</td>
                    <td className="px-6 py-3 text-right">
                      <Link
                        href={`/instruments/${inst.symbol}`}
                        className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-slate-100 text-slate-400 group-hover:bg-primary-100 group-hover:text-primary-600 transition-colors"
                      >
                        <ChevronRight size={16} />
                      </Link>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {!isLoading && !isError && totalPages > 1 && (
        <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-between">
          <span className="text-sm text-slate-500">
            Toplam {total} enstrüman • {((page - 1) * PAGE_SIZE) + 1}–{Math.min(page * PAGE_SIZE, total)} gösteriliyor
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1.5 text-sm font-medium text-navy-700 bg-white border border-slate-200 rounded-md hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              ← Önceki
            </button>
            <span className="px-3 py-1.5 text-sm font-medium text-navy-900 bg-slate-100 rounded-md">
              {page} / {totalPages}
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-3 py-1.5 text-sm font-medium text-navy-700 bg-white border border-slate-200 rounded-md hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Sonraki →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function MarketsPage() {
  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-navy-900 tracking-tight">Piyasalar</h1>
        <p className="text-navy-700 mt-1">BIST 100 enstrümanlarını keşfedin.</p>
      </div>
      <MarketsTable />
    </div>
  );
}

"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetchApi } from "@/lib/api";
import { Search, ChevronRight } from "lucide-react";
import { useState } from "react";

function MarketsTable() {
  const [searchTerm, setSearchTerm] = useState("");
  
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['instruments', 'BIST100'],
    queryFn: () => fetchApi('/api/v1/instruments?page=1&size=100'),
  });

  const instruments = (data as any)?.items || [];
  
  const filtered = instruments.filter((inst: any) => 
    inst.symbol.toLowerCase().includes(searchTerm.toLowerCase()) || 
    (inst.name && inst.name.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const symbolsToFetch = filtered.slice(0, 100).map((i: any) => i.symbol).join(',');

  const { data: quotesData, isError: isQuotesError } = useQuery({
    queryKey: ['quotes_batch', symbolsToFetch],
    queryFn: () => symbolsToFetch ? fetchApi(`/api/v1/instruments/quotes/batch?symbols=${symbolsToFetch}`) : Promise.resolve({}),
    enabled: !!symbolsToFetch,
    refetchInterval: 15000,
  });

  return (
    <div className="bg-surface rounded-xl border border-navy-800/10 shadow-sm overflow-hidden">
      <div className="p-4 border-b border-navy-800/10 flex flex-col sm:flex-row gap-4 justify-between items-center bg-slate-50">
        <div className="relative w-full sm:w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input 
            type="text" 
            placeholder="Sembol veya şirket ara..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div className="flex gap-2 w-full sm:w-auto overflow-x-auto pb-2 sm:pb-0">
          <button className="px-3 py-1.5 bg-navy-900 text-white text-sm font-medium rounded-md whitespace-nowrap">BIST 100</button>
          <button className="px-3 py-1.5 bg-white border border-slate-200 text-navy-700 text-sm font-medium rounded-md whitespace-nowrap opacity-50 cursor-not-allowed">FX</button>
          <button className="px-3 py-1.5 bg-white border border-slate-200 text-navy-700 text-sm font-medium rounded-md whitespace-nowrap opacity-50 cursor-not-allowed">Kripto</button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white border-b border-navy-800/10 text-xs uppercase text-navy-700/60 font-semibold">
              <th className="px-6 py-4">Sembol</th>
              <th className="px-6 py-4 hidden md:table-cell">Şirket</th>
              <th className="px-6 py-4 text-right">Fiyat</th>
              <th className="px-6 py-4 text-right">Değişim</th>
              <th className="px-6 py-4 hidden sm:table-cell">Kategori</th>
              <th className="px-6 py-4"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {isError ? (
              <tr>
                <td colSpan={6} className="p-8 text-center text-danger-600 bg-danger-50">
                  <div className="font-semibold mb-1">Veri yüklenirken hata oluştu</div>
                  <div className="text-sm opacity-80">Lütfen daha sonra tekrar deneyin veya oturumunuzu kontrol edin.</div>
                </td>
              </tr>
            ) : isLoading ? (
              <tr><td colSpan={6} className="p-8 text-center text-slate-500">Yükleniyor...</td></tr>
            ) : filtered.length === 0 ? (
              <tr><td colSpan={6} className="p-8 text-center text-slate-500">Sonuç bulunamadı.</td></tr>
            ) : (
              filtered.map((inst: any) => {
                const q = (quotesData as any)?.[inst.symbol];
                const price = q?.price != null ? Number(q.price).toFixed(2) + ' ₺' : '---';
                const change = q?.price != null && q?.previous_close != null 
                  ? (Number(q.price) - Number(q.previous_close)).toFixed(2) 
                  : '---';
                const changePct = q?.change_pct != null ? Number(q.change_pct).toFixed(2) + '%' : '---';
                const isPositive = q?.change_pct != null && Number(q.change_pct) >= 0;
                
                return (
                  <tr key={inst.symbol} className="hover:bg-slate-50 group transition-colors">
                    <td className="px-6 py-3 font-bold text-navy-900">
                      <Link href={`/instruments/${inst.symbol}`} className="hover:text-primary-600 flex items-center gap-2">
                        {inst.symbol}
                        {q?.data_state && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded-sm bg-slate-100 text-slate-500 font-medium">
                            {q.data_state === 'DELAYED' ? 'Gecikmeli' : q.data_state === 'EOD' ? 'GÜN SONU' : 'Canlı'}
                          </span>
                        )}
                      </Link>
                    </td>
                    <td className="px-6 py-3 text-sm text-navy-700/80 hidden md:table-cell max-w-[200px] truncate">
                      {inst.name !== inst.symbol ? inst.name : ''}
                    </td>
                    <td className="px-6 py-3 text-right font-medium text-navy-900">
                      {price}
                    </td>
                    <td className={`px-6 py-3 text-right font-medium ${isPositive ? 'text-success-600' : q?.change_pct != null ? 'text-danger-600' : 'text-slate-500'}`}>
                      {q?.change_pct != null && (isPositive ? '+' : '')}{change} ({changePct})
                    </td>
                    <td className="px-6 py-3 text-sm text-slate-500 hidden sm:table-cell">
                      Hisse
                    </td>
                    <td className="px-6 py-3 text-right">
                      <Link href={`/instruments/${inst.symbol}`} className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-slate-100 text-slate-400 group-hover:bg-primary-100 group-hover:text-primary-600 transition-colors">
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
    </div>
  );
}

export default function MarketsPage() {
  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-navy-900 tracking-tight">Piyasalar</h1>
        <p className="text-navy-700 mt-1">Takip edilen enstrümanları keşfedin.</p>
      </div>

      <MarketsTable />
    </div>
  );
}

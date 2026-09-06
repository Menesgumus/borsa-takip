"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";
import { Search } from "lucide-react";

async function fetchInstruments(page: number, search: string) {
  const params = new URLSearchParams({ page: page.toString(), size: "20" });
  if (search) params.append("search", search);
  
  const res = await fetch(`/api/v1/instruments?${params.toString()}`);
  if (!res.ok) throw new Error("Failed to fetch markets");
  return res.json();
}

export default function MarketsPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["instruments", "list", page, search],
    queryFn: () => fetchInstruments(page, search),
    placeholderData: (prev) => prev,
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className="text-2xl font-bold text-gray-800">Piyasalar</h2>
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Sembol veya isim ara..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-50 border-b border-gray-200 text-gray-600">
            <tr>
              <th className="p-4 font-semibold">Sembol</th>
              <th className="p-4 font-semibold">İsim</th>
              <th className="p-4 font-semibold">Borsa</th>
              <th className="p-4 font-semibold">Tür</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {isLoading ? (
              <tr>
                <td colSpan={4} className="p-4 text-center text-gray-500">Yükleniyor...</td>
              </tr>
            ) : data?.items?.length === 0 ? (
              <tr>
                <td colSpan={4} className="p-4 text-center text-gray-500">Sonuç bulunamadı.</td>
              </tr>
            ) : (
              data?.items?.map((inst: any) => (
                <tr key={inst.symbol} className="hover:bg-gray-50 transition-colors">
                  <td className="p-4">
                    <Link href={`/instruments/${inst.symbol}`} className="font-semibold text-blue-600 hover:underline">
                      {inst.symbol}
                    </Link>
                  </td>
                  <td className="p-4 text-gray-800">{inst.name}</td>
                  <td className="p-4 text-gray-500">{inst.exchange}</td>
                  <td className="p-4 text-gray-500">{inst.instrument_type}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {data && data.total > 20 && (
        <div className="flex justify-between items-center text-sm text-gray-600">
          <div>
            Toplam {data.total} sonuçtan {(page - 1) * 20 + 1}-{Math.min(page * 20, data.total)} gösteriliyor.
          </div>
          <div className="flex gap-2">
            <button
              disabled={page === 1}
              onClick={() => setPage(p => p - 1)}
              className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
            >
              Önceki
            </button>
            <button
              disabled={page * 20 >= data.total}
              onClick={() => setPage(p => p + 1)}
              className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
            >
              Sonraki
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

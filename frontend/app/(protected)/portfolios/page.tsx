"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Plus, Briefcase, TrendingUp, WifiOff } from "lucide-react";
import { useNetwork } from "@/components/NetworkProvider";

export default function PortfoliosPage() {
  const { isOnline } = useNetwork();
  const { data: portfolios, isLoading } = useQuery({
    queryKey: ["portfolios"],
    queryFn: async () => {
      const res = await fetch("/api/v1/portfolios/");
      if (!res.ok) throw new Error("Failed to fetch portfolios");
      return res.json();
    },
  });

  if (isLoading) return <div className="p-6">Yükleniyor...</div>;

  return (
    <div className="space-y-6 max-w-4xl mx-auto p-4">
      <div className="flex flex-col md:flex-row justify-between items-center bg-white p-6 rounded-lg shadow-sm border border-gray-200 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Briefcase size={24} className="text-blue-600" />
            Portföylerim
          </h1>
          <p className="text-gray-500">Real ve Paper portföylerinizi yönetin</p>
        </div>
        <button 
          onClick={() => {
            if (!isOnline) {
              alert("Bu işlem internet bağlantısı gerektiriyor.");
            } else {
              // open modal
            }
          }}
          className={`flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium w-full md:w-auto min-h-[44px] ${
            isOnline ? "bg-blue-600 text-white hover:bg-blue-700" : "bg-gray-300 text-gray-500 cursor-not-allowed"
          }`}
        >
          <Plus size={18} /> Yeni Portföy
        </button>
      </div>

      {!isOnline && portfolios && portfolios.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-4 rounded-lg flex gap-3 shadow-sm">
          <WifiOff className="shrink-0" />
          <div>
            <strong>STALE / LAST KNOWN DATA</strong>
            <p className="text-sm">Çevrimdışısınız. Aşağıdaki portföy listesi son bilinen önbellek verisidir ve güncel olmayabilir. Finansal işlem ekleme (BUY/SELL) çevrimdışıyken devre dışıdır.</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {portfolios?.length === 0 ? (
          <div className="col-span-1 md:col-span-2 text-center p-12 bg-white rounded-lg border border-gray-200 text-gray-500">
            Henüz portföyünüz bulunmuyor. Yeni bir tane oluşturun.
          </div>
        ) : (
          portfolios?.map((p: any) => (
            <Link href={`/portfolios/${p.id}`} key={p.id}>
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:border-blue-300 hover:shadow-md transition cursor-pointer relative">
                {!isOnline && (
                  <span className="absolute top-2 right-2 bg-yellow-100 text-yellow-800 text-[10px] font-bold px-2 py-1 rounded">STALE</span>
                )}
                <div className="flex justify-between items-start mb-4">
                  <h2 className="text-xl font-bold text-gray-900">{p.name}</h2>
                  <span className={`px-2 py-1 text-xs font-semibold rounded ${
                    p.portfolio_type === "REAL" ? "bg-purple-100 text-purple-800" : "bg-gray-100 text-gray-800"
                  }`}>
                    {p.portfolio_type}
                  </span>
                </div>
                <div className="text-sm text-gray-500 flex items-center gap-1">
                  <TrendingUp size={16} /> Para Birimi: {p.currency}
                </div>
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
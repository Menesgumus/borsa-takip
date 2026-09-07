"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Plus, Briefcase, TrendingUp } from "lucide-react";

export default function PortfoliosPage() {
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
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Briefcase size={24} className="text-blue-600" />
            Portföylerim
          </h1>
          <p className="text-gray-500">Real ve Paper portföylerinizi yönetin</p>
        </div>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium">
          <Plus size={18} /> Yeni Portföy
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {portfolios?.length === 0 ? (
          <div className="col-span-2 text-center p-12 bg-white rounded-lg border border-gray-200 text-gray-500">
            Henüz portföyünüz bulunmuyor. Yeni bir tane oluşturun.
          </div>
        ) : (
          portfolios?.map((p: any) => (
            <Link href={/portfolios/} key={p.id}>
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:border-blue-300 hover:shadow-md transition cursor-pointer">
                <div className="flex justify-between items-start mb-4">
                  <h2 className="text-xl font-bold text-gray-900">{p.name}</h2>
                  <span className={px-2 py-1 text-xs font-semibold rounded }>
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

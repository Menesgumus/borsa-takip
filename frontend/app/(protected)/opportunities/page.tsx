"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetchApi } from "@/lib/api";
import { ChevronRight, Target, ShieldAlert, Star } from "lucide-react";

export default function OpportunitiesPage() {
  const { data: instruments, isLoading } = useQuery({
    queryKey: ["opportunities"],
    queryFn: () => fetchApi("/api/v1/opportunities?limit=10"),
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-500 max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-navy-900 tracking-tight">Fırsatlar</h1>
        <p className="text-navy-700 mt-1">Sistem tarafından belirlenen güncel potansiyeller.</p>
      </div>

      <div className="bg-primary-50 border border-primary-100 rounded-xl p-5 mb-8 flex gap-4">
        <Target className="text-primary-600 shrink-0 mt-0.5" />
        <div className="text-sm text-navy-800">
          <strong className="block text-navy-900 mb-1">Fırsat Puanlaması Hakkında</strong>
          Piyasa Fırsat Puanı (Raw Market Score), teknik ve temel analize dayalı mutlak pazar potansiyelini gösterir. 
          Kişisel Uyum (User Fit), sizin risk toleransınıza ve portföy yoğunluğunuza göre bu fırsatın sizin için ne kadar uygun olduğunu belirtir.
          <em> En yüksek puan her zaman kesin &quot;Al&quot; demek değildir.</em>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          [1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="h-48 bg-slate-100 animate-pulse rounded-xl border border-slate-200"></div>
          ))
        ) : instruments && (instruments as any).length > 0 ? (
          (instruments as any).map((inst: any) => (
            <Link key={inst.symbol} href={`/instruments/${inst.symbol}`} className="bg-surface rounded-xl p-6 border border-navy-800/10 shadow-sm hover:shadow-md transition-all group">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-bold text-navy-900 group-hover:text-primary-600 transition-colors">{inst.symbol}</h3>
                  <p className="text-sm text-navy-700/60 truncate max-w-[150px]">{inst.name || 'Hisse Senedi'}</p>
                </div>
                <div className="flex gap-1">
                  <span className="px-2 py-1 bg-success-50 text-success-700 text-xs font-bold rounded">AL</span>
                </div>
              </div>

              <div className="space-y-3 mt-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-navy-700/80">Piyasa Fırsat Puanı</span>
                  <div className="flex items-center gap-1 font-bold text-navy-900">
                    <Star size={14} className="text-amber-400 fill-amber-400" />
                    {Number(inst.decision?.overall_market_score || 85).toFixed(0)}/100
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-navy-700/80">Kişisel Uyum</span>
                  <span className="font-bold text-primary-600">
                    % {Number(inst.decision?.portfolio_fit_score || 90).toFixed(0)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-navy-700/80">Veri Kalitesi</span>
                  <span className="text-sm font-medium text-navy-900">
                    {Number(inst.decision?.data_quality_score || 100).toFixed(0)}/100
                  </span>
                </div>
              </div>

              <div className="mt-5 pt-4 border-t border-slate-100 text-sm font-medium text-primary-600 flex items-center justify-between">
                Detayları İncele
                <ChevronRight size={16} />
              </div>
            </Link>
          ))
        ) : (
          <div className="col-span-full bg-surface rounded-xl p-12 border border-navy-800/10 shadow-sm text-center">
            <ShieldAlert className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-navy-900 mb-1">Şu An Fırsat Bulunmuyor</h3>
            <p className="text-navy-700">Piyasa koşulları ve veri kalitesi kriterlerini karşılayan yeni fırsatlar burada listelenecektir.</p>
          </div>
        )}
      </div>
    </div>
  );
}

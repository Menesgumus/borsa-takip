"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchApi } from "@/lib/api";
import { AlertCircle, RefreshCw, PieChart, ChevronRight } from "lucide-react";

type RiskState =
  | { kind: "LOADING" }
  | { kind: "ERROR"; message: string }
  | { kind: "TIMEOUT" }
  | { kind: "NO_PORTFOLIO" }
  | { kind: "ONE_PORTFOLIO"; id: number }
  | { kind: "MULTIPLE_PORTFOLIOS"; portfolios: any[] };

export default function RiskPage() {
  const router = useRouter();
  const [redirecting, setRedirecting] = useState(false);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["portfolios"],
    queryFn: () => fetchApi("/api/v1/portfolios/"),
    staleTime: 30_000,
    retry: (failureCount: number, err: any) => {
      if (err?.status >= 400 && err?.status < 500) return false;
      return failureCount < 1;
    },
  });

  const portfolios: any[] = Array.isArray(data) ? data : [];

  let state: RiskState;
  if (isLoading) {
    state = { kind: "LOADING" };
  } else if (isError) {
    const errMsg = (error as any)?.message || "Portföy verileri alınamadı.";
    state = errMsg.toLowerCase().includes("timeout") || errMsg.toLowerCase().includes("abort")
      ? { kind: "TIMEOUT" }
      : { kind: "ERROR", message: errMsg };
  } else if (portfolios.length === 0) {
    state = { kind: "NO_PORTFOLIO" };
  } else if (portfolios.length === 1) {
    state = { kind: "ONE_PORTFOLIO", id: portfolios[0].id };
  } else {
    state = { kind: "MULTIPLE_PORTFOLIOS", portfolios };
  }

  // Single portfolio: auto-redirect once, no flash loop
  useEffect(() => {
    if (state.kind === "ONE_PORTFOLIO" && !redirecting) {
      setRedirecting(true);
      router.replace(`/portfolios/${state.id}/risk`);
    }
  }, [state, redirecting, router]);

  // ── LOADING ───────────────────────────────────────────────────────────────
  if (state.kind === "LOADING" || (state.kind === "ONE_PORTFOLIO" && redirecting)) {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] gap-4 text-slate-500">
        <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm">
          {state.kind === "ONE_PORTFOLIO" ? "Risk yönetimi sayfasına yönlendiriliyorsunuz..." : "Portföyler yükleniyor..."}
        </p>
      </div>
    );
  }

  // ── TIMEOUT ───────────────────────────────────────────────────────────────
  if (state.kind === "TIMEOUT") {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] gap-4">
        <AlertCircle className="text-amber-500" size={36} />
        <h2 className="text-lg font-semibold text-navy-900">Bağlantı zaman aşımı</h2>
        <p className="text-sm text-slate-500 text-center max-w-sm">
          Portföy verisi 8 saniye içinde alınamadı. İnternet bağlantınızı kontrol edin.
        </p>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
        >
          <RefreshCw size={15} /> Tekrar Dene
        </button>
      </div>
    );
  }

  // ── ERROR ─────────────────────────────────────────────────────────────────
  if (state.kind === "ERROR") {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] gap-4">
        <AlertCircle className="text-danger-500" size={36} />
        <h2 className="text-lg font-semibold text-navy-900">Hata oluştu</h2>
        <p className="text-sm text-slate-500 text-center max-w-sm">{state.message}</p>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
        >
          <RefreshCw size={15} /> Tekrar Dene
        </button>
      </div>
    );
  }

  // ── NO PORTFOLIO ──────────────────────────────────────────────────────────
  if (state.kind === "NO_PORTFOLIO") {
    return (
      <div className="flex flex-col items-center justify-center h-[50vh] gap-6 text-center max-w-md mx-auto">
        <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center">
          <PieChart className="text-slate-400" size={32} />
        </div>
        <div>
          <h2 className="text-xl font-bold text-navy-900 mb-2">Henüz portföy yok</h2>
          <p className="text-slate-500 text-sm leading-relaxed">
            Risk yönetimi, bir portföy oluşturulduktan sonra aktif olur. Önce bir portföy oluşturun.
          </p>
        </div>
        <Link
          href="/portfolios"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white text-sm font-semibold rounded-lg hover:bg-primary-700 transition-colors"
        >
          Portföy Oluştur <ChevronRight size={16} />
        </Link>
      </div>
    );
  }

  // ── MULTIPLE PORTFOLIOS ───────────────────────────────────────────────────
  if (state.kind === "MULTIPLE_PORTFOLIOS") {
    return (
      <div className="space-y-6 max-w-2xl mx-auto">
        <div>
          <h1 className="text-2xl font-bold text-navy-900">Risk Yönetimi</h1>
          <p className="text-navy-700 mt-1">Risk analizi için bir portföy seçin.</p>
        </div>
        <div className="grid gap-4">
          {state.portfolios.map((p) => (
            <Link
              key={p.id}
              href={`/portfolios/${p.id}/risk`}
              className="flex items-center justify-between p-5 bg-surface rounded-xl border border-navy-800/10 shadow-sm hover:border-primary-300 hover:shadow-md transition-all group"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                  <PieChart className="text-primary-600" size={20} />
                </div>
                <div>
                  <div className="font-semibold text-navy-900 group-hover:text-primary-600 transition-colors">
                    {p.name}
                  </div>
                  <div className="text-sm text-slate-500">
                    {p.portfolio_type === "PAPER" ? "Kağıt Portföy" : p.portfolio_type}
                  </div>
                </div>
              </div>
              <ChevronRight className="text-slate-400 group-hover:text-primary-500 transition-colors" size={20} />
            </Link>
          ))}
        </div>
      </div>
    );
  }

  return null;
}

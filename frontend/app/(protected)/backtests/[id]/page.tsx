"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { ArrowLeft, CheckCircle, AlertTriangle, ShieldAlert } from "lucide-react";
import Link from "next/link";

export default function BacktestResultPage() {
  const { id } = useParams();

  const { data: job, isLoading: loadingJob } = useQuery({
    queryKey: ["backtest", id],
    queryFn: async () => {
      const res = await fetch(`/api/v1/backtests/${id}`);
      if (!res.ok) throw new Error("Job not found");
      return res.json();
    }
  });

  const { data: result, isLoading: loadingResult } = useQuery({
    queryKey: ["backtest-result", id],
    queryFn: async () => {
      const res = await fetch(`/api/v1/backtests/${id}/result`);
      if (!res.ok) throw new Error("Result not found");
      return res.json();
    },
    enabled: !!job && job.status === "COMPLETED"
  });

  if (loadingJob) return <div className="p-8">Yükleniyor...</div>;

  const biasAudit = result?.bias_audit ? JSON.parse(result.bias_audit) : null;
  const limitations = result?.limitations ? JSON.parse(result.limitations) : [];

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <Link href="/backtests" className="flex items-center gap-2 text-gray-500 hover:text-black mb-6">
        <ArrowLeft size={16} /> Geri Dön
      </Link>

      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold">{job.strategy_name} <span className="text-gray-400 font-normal text-xl">v{job.strategy_version}</span></h1>
          <p className="text-gray-500 mt-1">
            Simülasyon Dönemi: {new Date(job.start_date).toLocaleDateString()} - {new Date(job.end_date).toLocaleDateString()}
          </p>
        </div>
        <div className={`px-4 py-2 rounded-lg font-bold border ${result?.validation_state === 'LIMITED' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' : 'bg-green-50 text-green-700 border-green-200'}`}>
          Durum: {result?.validation_state || job.status}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-500">Toplam Getiri</div>
          <div className="text-3xl font-bold text-gray-800">{result?.total_return_pct || '0'}%</div>
        </div>
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-500">Max Drawdown</div>
          <div className="text-3xl font-bold text-red-600">{result?.max_drawdown_pct || '0'}%</div>
        </div>
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <div className="text-sm text-gray-500">İşlem Ücretleri & Slippage</div>
          <div className="text-3xl font-bold text-gray-800">₺{result?.fees_paid || '0.00'}</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <h2 className="font-bold text-lg mb-4 flex items-center gap-2">
            <ShieldAlert className="text-blue-500" /> Katı Bias Otoritesi
          </h2>
          <div className="space-y-3">
            {biasAudit && Object.entries(biasAudit).map(([key, value]: any) => (
              <div key={key} className="flex justify-between items-center text-sm border-b border-gray-50 pb-2">
                <span className="font-mono text-gray-600">{key}</span>
                {value === 'PASS' ? (
                  <span className="text-green-600 flex items-center gap-1"><CheckCircle size={14}/> PASS</span>
                ) : (
                  <span className="text-yellow-600 flex items-center gap-1"><AlertTriangle size={14}/> {value}</span>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <h2 className="font-bold text-lg mb-4 flex items-center gap-2">
            <AlertTriangle className="text-red-500" /> Sınırlamalar (Limitations)
          </h2>
          {limitations.length === 0 ? (
            <p className="text-gray-500 text-sm">Raporlanan bir sınırlama yok.</p>
          ) : (
            <ul className="space-y-2">
              {limitations.map((lim: string, i: number) => (
                <li key={i} className="bg-red-50 text-red-800 px-3 py-2 rounded text-sm font-mono">{lim}</li>
              ))}
            </ul>
          )}
          <p className="text-xs text-gray-400 mt-6">
            * Geçmiş performans gelecekteki getiriyi garanti etmez. Stratejiler Out-Of-Sample dönemlerde aynı başarıyı göstermeyebilir.
          </p>
        </div>
      </div>
    </div>
  );
}

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Activity, Play, Plus, AlertTriangle, WifiOff } from "lucide-react";
import { useState } from "react";
import Link from "next/link";
import { useNetwork } from "@/components/NetworkProvider";

export default function BacktestsPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const { isOnline } = useNetwork();

  const { data: jobs, isLoading } = useQuery({
    queryKey: ["backtests"],
    queryFn: async () => {
      const res = await fetch("/api/v1/backtests");
      if (!res.ok) throw new Error("Failed to load");
      return res.json();
    }
  });

  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await fetch("/api/v1/backtests/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      if (!res.ok) throw new Error("Creation failed");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["backtests"] });
      setShowForm(false);
    }
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isOnline) {
      alert("İnternet bağlantısı olmadan yeni simülasyon başlatılamaz.");
      return;
    }
    createMutation.mutate({
      strategy_name: "DecisionEngineV1",
      strategy_version: "1.0",
      start_date: "2023-01-01T00:00:00Z",
      end_date: "2023-12-31T00:00:00Z",
      initial_capital: 100000,
      commission_pct: 0.001,
      slippage_pct: 0.0005
    });
  };

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Activity className="text-blue-600" /> Backtest Motoru
          </h1>
          <p className="text-gray-600">Event-safe point-in-time geçmiş simülasyon ve analiz.</p>
        </div>
        <button 
          onClick={() => setShowForm(!showForm)} 
          disabled={!isOnline}
          className={`px-4 py-2 rounded-lg flex items-center justify-center gap-2 min-h-[44px] w-full md:w-auto ${isOnline ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-500'}`}
        >
          {showForm ? "İptal" : <><Plus size={16} /> Yeni Simülasyon</>}
        </button>
      </div>

      {!isOnline && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-4 rounded-lg flex gap-3 shadow-sm">
          <WifiOff className="shrink-0" />
          <div>
            <strong>STALE / LAST KNOWN DATA</strong>
            <p className="text-sm">Çevrimdışısınız. Yeni simülasyon başlatılamaz. Gördüğünüz sonuçlar son bilinen verilerdir.</p>
          </div>
        </div>
      )}

      {showForm && isOnline && (
        <form onSubmit={handleCreate} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="font-bold text-lg mb-4">Yeni Backtest (V1 Mock)</h2>
          <p className="text-sm text-gray-500 mb-4">
            V1 simülatörü deterministic policy ile Karar Motoru (Phase 10) sonuçlarını 2023 yılı için test eder.
          </p>
          <button type="submit" disabled={createMutation.isPending} className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2 min-h-[44px] w-full md:w-auto">
            <Play size={16} /> Simülasyonu Başlat
          </button>
        </form>
      )}

      {/* Desktop Table (Hidden on small screens) */}
      <div className="hidden md:block bg-white rounded-lg shadow-sm border border-gray-200">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-200 text-gray-500 text-sm">
            <tr>
              <th className="p-4">Strateji</th>
              <th className="p-4">Tarih Aralığı</th>
              <th className="p-4">Durum</th>
              <th className="p-4 text-right">İşlemler</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {jobs?.map((job: any) => (
              <tr key={job.id} className="hover:bg-gray-50">
                <td className="p-4">
                  <div className="font-bold">{job.strategy_name}</div>
                  <div className="text-xs text-gray-500">v{job.strategy_version}</div>
                </td>
                <td className="p-4 text-sm text-gray-600">
                  {new Date(job.start_date).toLocaleDateString()} - {new Date(job.end_date).toLocaleDateString()}
                </td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    job.status === 'COMPLETED' ? 'bg-green-100 text-green-700' : 
                    job.status === 'RUNNING' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'
                  }`}>
                    {job.status}
                  </span>
                </td>
                <td className="p-4 text-right">
                  {job.status === 'COMPLETED' && (
                    <Link href={`/backtests/${job.id}`} className="text-blue-600 text-sm font-semibold hover:underline min-h-[44px] flex items-center justify-end">
                      Sonuçları Gör &rarr;
                    </Link>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {jobs?.length === 0 && <div className="p-8 text-center text-gray-500">Kayıtlı backtest bulunamadı.</div>}
      </div>

      {/* Mobile Cards (Hidden on md+ screens) */}
      <div className="md:hidden space-y-4">
        {jobs?.map((job: any) => (
          <div key={job.id} className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="flex justify-between items-start mb-2">
              <div>
                <div className="font-bold text-lg">{job.strategy_name}</div>
                <div className="text-sm text-gray-500">v{job.strategy_version}</div>
              </div>
              <span className={`px-2 py-1 rounded text-[10px] font-bold ${
                    job.status === 'COMPLETED' ? 'bg-green-100 text-green-700' : 
                    job.status === 'RUNNING' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'
                  }`}>
                {job.status}
              </span>
            </div>
            <div className="text-sm text-gray-600 mb-4">
              {new Date(job.start_date).toLocaleDateString()} - {new Date(job.end_date).toLocaleDateString()}
            </div>
            {job.status === 'COMPLETED' && (
              <Link href={`/backtests/${job.id}`} className="flex justify-center items-center w-full bg-blue-50 text-blue-600 font-bold min-h-[44px] rounded-lg border border-blue-100">
                Sonuçları Gör &rarr;
              </Link>
            )}
          </div>
        ))}
        {jobs?.length === 0 && <div className="p-8 text-center text-gray-500 bg-white rounded-lg border border-gray-200">Kayıtlı backtest bulunamadı.</div>}
      </div>
    </div>
  );
}
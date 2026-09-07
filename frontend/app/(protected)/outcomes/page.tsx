"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { LineChart, BarChart2, ShieldAlert, Zap } from "lucide-react";
import { useState } from "react";

export default function OutcomesPage() {
  const queryClient = useQueryClient();

  const { data: versions, isLoading: loadingVersions } = useQuery({
    queryKey: ["strategy-versions"],
    queryFn: async () => {
      const res = await fetch("/api/v1/outcomes/strategy-versions");
      if (!res.ok) throw new Error("Failed to load");
      return res.json();
    }
  });

  const { data: recentOutcomes, isLoading: loadingOutcomes } = useQuery({
    queryKey: ["recent-outcomes"],
    queryFn: async () => {
      const res = await fetch("/api/v1/outcomes/recent");
      if (!res.ok) throw new Error("Failed to load");
      return res.json();
    }
  });

  const triggerMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch("/api/v1/outcomes/trigger-tracker", { method: "POST" });
      if (!res.ok) throw new Error("Tracker failed");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recent-outcomes"] });
      queryClient.invalidateQueries({ queryKey: ["strategy-versions"] });
    }
  });

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <LineChart className="text-indigo-600" /> Strateji Karar Performansı
          </h1>
          <p className="text-gray-600">Geçmiş kararların T+1, T+5, T+20, T+60 ileriye dönük gerçekleşen getirileri.</p>
        </div>
        <button 
          onClick={() => triggerMutation.mutate()} 
          disabled={triggerMutation.isPending}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <Zap size={16} /> Hesapla (Trigger Worker)
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center rounded-t-lg">
          <h2 className="font-bold text-lg text-gray-800">Şampiyon / Challenger Modeli</h2>
        </div>
        <div className="p-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4 flex gap-3 text-yellow-800 text-sm">
            <ShieldAlert className="shrink-0" />
            <div>
              <strong>Otomatik Terfi Durduruldu:</strong> Gerçek veri seti limiti (Phase 15 Waiver) nedeniyle Challenger model otomatik olarak Şampiyon olamaz (Auto-Promotion yasaklandı). Strateji performansını test edebilirsiniz ancak sadece <i>Shadow Mode</i> aktif.
            </div>
          </div>

          <table className="w-full text-left">
            <thead className="bg-gray-100 text-gray-600 text-xs uppercase font-semibold">
              <tr>
                <th className="p-3 rounded-tl-lg">Model</th>
                <th className="p-3">Versiyon</th>
                <th className="p-3">Statü</th>
                <th className="p-3 rounded-tr-lg">Terfi Notu</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 text-sm">
              {versions?.map((v: any) => (
                <tr key={v.id}>
                  <td className="p-3 font-bold">{v.name}</td>
                  <td className="p-3 font-mono">{v.version}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      v.status === 'CHAMPION' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                    }`}>
                      {v.status}
                    </span>
                  </td>
                  <td className="p-3 text-red-600 font-mono text-xs">{v.promotion_reason || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg">
          <h2 className="font-bold text-lg text-gray-800">Son Değerlendirilen Kararlar</h2>
        </div>
        
        {loadingOutcomes ? (
          <div className="p-6 text-gray-500">Yükleniyor...</div>
        ) : recentOutcomes?.length === 0 ? (
          <div className="p-6 text-center text-gray-500">Henüz değerlendirilmiş karar bulunmuyor.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-50 border-b border-gray-200 text-gray-500">
                <tr>
                  <th className="p-4">Karar ID</th>
                  <th className="p-4">T+1 Getiri</th>
                  <th className="p-4">T+5 Getiri</th>
                  <th className="p-4">T+20 Getiri</th>
                  <th className="p-4">T+60 Getiri</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {recentOutcomes?.map((out: any) => (
                  <tr key={out.id} className="hover:bg-gray-50">
                    <td className="p-4 font-mono">#{out.decision_id}</td>
                    <td className="p-4 font-mono">{out.return_t1}%</td>
                    <td className="p-4 font-mono">{out.return_t5}%</td>
                    <td className="p-4 font-mono">{out.return_t20}%</td>
                    <td className="p-4 font-mono">{out.return_t60}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

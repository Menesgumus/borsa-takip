"use client";

import { useQuery } from "@tanstack/react-query";
import { Brain, Activity, Target, Flame } from "lucide-react";

export default function BehaviorPage() {
  const { data: profile, isLoading: loadingProf } = useQuery({
    queryKey: ["behavior-profile"],
    queryFn: async () => {
      const res = await fetch("/api/v1/behavior/profile");
      if (!res.ok) throw new Error("Failed to load");
      return res.json();
    }
  });

  const { data: insights, isLoading: loadingIns } = useQuery({
    queryKey: ["behavior-insights"],
    queryFn: async () => {
      const res = await fetch("/api/v1/behavior/insights");
      if (!res.ok) throw new Error("Failed to load");
      return res.json();
    }
  });

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Brain className="text-purple-600" /> Kişisel Karar Davranışları
          </h1>
          <p className="text-gray-600">Alım-satım alışkanlıklarınız, FOMO riskiniz ve sabır metrikleriniz.</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center gap-2 text-gray-500 mb-2">
            <Flame size={18} className="text-orange-500" /> FOMO Eğilimi
          </div>
          <div className="text-3xl font-bold text-gray-800">{profile?.fomo_tendency_score || '0.00'}/100</div>
          <p className="text-xs text-gray-400 mt-2">Ani yükseliş sonrası plan dışı giriş ihtimali</p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center gap-2 text-gray-500 mb-2">
            <Activity size={18} className="text-green-500" /> Sabır & Vade Uyumu
          </div>
          <div className="text-3xl font-bold text-gray-800">{profile?.patience_score || '0.00'}/100</div>
          <p className="text-xs text-gray-400 mt-2">Planlanan hedefe kadar bekleyebilme oranı</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center gap-2 text-gray-500 mb-2">
            <Target size={18} className="text-blue-500" /> Konsantrasyon Riski
          </div>
          <div className="text-3xl font-bold text-gray-800">{profile?.concentration_risk || '0.00'}/100</div>
          <p className="text-xs text-gray-400 mt-2">Tek varlığa ayrılan riskli portföy ağırlığı</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg">
          <h2 className="font-bold text-lg text-gray-800">Trade Insight Geçmişi</h2>
        </div>
        
        {loadingIns ? (
          <div className="p-6 text-gray-500">Yükleniyor...</div>
        ) : insights?.length === 0 ? (
          <div className="p-6 text-center text-gray-500">Henüz davranışsal bir analiz oluşmadı.</div>
        ) : (
          <div className="divide-y divide-gray-100">
            {insights?.map((ins: any) => (
              <div key={ins.id} className="p-4 flex gap-4">
                <div className="mt-1">
                  {ins.insight_type.includes('FOMO') ? (
                    <Flame className="text-orange-500" size={20} />
                  ) : (
                    <Brain className="text-purple-500" size={20} />
                  )}
                </div>
                <div>
                  <h3 className="font-bold text-sm text-gray-800">{ins.insight_type}</h3>
                  <p className="text-gray-600 text-sm mt-1">{ins.description}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

"use client";

import { useQuery } from "@tanstack/react-query";
import { Bell, BellOff, Info } from "lucide-react";
import { useState } from "react";

export default function AlertsPage() {
  const { data: rules, isLoading: loadingRules } = useQuery({
    queryKey: ["alert-rules"],
    queryFn: async () => {
      const res = await fetch("/api/v1/alerts/rules");
      if (!res.ok) throw new Error("Failed to load rules");
      return res.json();
    }
  });

  const { data: notifications, isLoading: loadingNotifs } = useQuery({
    queryKey: ["notifications"],
    queryFn: async () => {
      const res = await fetch("/api/v1/alerts/notifications");
      if (!res.ok) throw new Error("Failed to load notifications");
      return res.json();
    }
  });

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-8">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2 mb-2">
          <Bell className="text-blue-600" /> Alarm ve Bildirim Merkezi
        </h1>
        <p className="text-gray-600">Fiyat, RSI, Haber ve Karar Motoru kurallarınızı yönetin.</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50 rounded-t-lg">
          <h2 className="font-bold text-lg text-gray-800">Alarm Kurallarınız</h2>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700">
            Yeni Kural Ekle
          </button>
        </div>
        
        {loadingRules ? (
          <div className="p-6 text-gray-500">Yükleniyor...</div>
        ) : rules?.length === 0 ? (
          <div className="p-6 text-center text-gray-500">Henüz alarm kuralı oluşturmadınız.</div>
        ) : (
          <div className="divide-y divide-gray-100">
            {rules?.map((rule: any) => (
              <div key={rule.id} className="p-4 flex justify-between items-center">
                <div>
                  <div className="font-bold text-gray-800 flex items-center gap-2">
                    {rule.alert_type} 
                    {rule.operator && <span className="bg-gray-100 px-1 rounded text-xs">{rule.operator}</span>} 
                    {rule.threshold && <span className="text-blue-600 font-mono">{rule.threshold}</span>}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Cooldown: {rule.cooldown_minutes} dk | 
                    Son Tetiklenme: {rule.last_triggered_at ? new Date(rule.last_triggered_at).toLocaleString() : "Hiç"}
                  </div>
                </div>
                <div>
                  {rule.is_enabled ? (
                    <span className="text-green-600 flex items-center gap-1 text-sm font-semibold">
                      <Bell size={16} /> Aktif
                    </span>
                  ) : (
                    <span className="text-gray-400 flex items-center gap-1 text-sm font-semibold">
                      <BellOff size={16} /> Pasif
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg">
          <h2 className="font-bold text-lg text-gray-800">Geçmiş Bildirimler (Notification History)</h2>
        </div>
        
        {loadingNotifs ? (
          <div className="p-6 text-gray-500">Yükleniyor...</div>
        ) : notifications?.length === 0 ? (
          <div className="p-6 text-center text-gray-500">Bildirim geçmişiniz boş.</div>
        ) : (
          <div className="divide-y divide-gray-100">
            {notifications?.map((n: any) => (
              <div key={n.id} className={`p-4 flex gap-4 ${n.is_read ? 'opacity-60' : 'bg-blue-50/30'}`}>
                <div className="mt-1">
                  <Info className="text-blue-500" size={20} />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-gray-800">{n.title}</h3>
                  <p className="text-gray-600 text-sm mt-1">{n.message}</p>
                  <div className="text-xs text-gray-400 mt-2">
                    {new Date(n.created_at).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

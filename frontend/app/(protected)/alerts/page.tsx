"use client";

import { useQuery } from "@tanstack/react-query";
import { Bell, BellOff, Info, Settings, Smartphone } from "lucide-react";
import { useState, useEffect } from "react";
import { useNetwork } from "@/components/NetworkProvider";

export default function AlertsPage() {
  const { isOnline } = useNetwork();
  const [pushStatus, setPushStatus] = useState<string>("default");

  useEffect(() => {
    if (typeof window !== "undefined" && "Notification" in window) {
      setPushStatus(Notification.permission);
    } else {
      setPushStatus("unsupported");
    }
  }, []);

  const requestPushPermission = async () => {
    if (pushStatus === "unsupported") return;
    try {
      const permission = await Notification.requestPermission();
      setPushStatus(permission);
    } catch (e) {
      console.error("Push permission request failed", e);
    }
  };

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
          <Bell className="text-blue-600" /> Alarm Merkezi
        </h1>
        <p className="text-gray-600">Fiyat, RSI ve Karar Motoru kurallarınızı yönetin.</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="flex items-center gap-3">
          <Smartphone className="text-gray-400" size={24} />
          <div>
            <h3 className="font-bold text-gray-800">Cihaz Bildirimleri (Web Push)</h3>
            <p className="text-xs text-gray-500">Alarmları uygulama kapalıyken bile alın.</p>
          </div>
        </div>
        <div>
          {pushStatus === "granted" ? (
            <span className="text-green-600 text-sm font-bold flex items-center gap-1"><Bell size={16}/> İzin Verildi</span>
          ) : pushStatus === "denied" ? (
            <span className="text-red-600 text-sm font-bold">Reddedildi</span>
          ) : pushStatus === "unsupported" ? (
            <span className="text-gray-400 text-sm">Tarayıcı desteklemiyor</span>
          ) : (
            <button onClick={requestPushPermission} className="bg-indigo-50 text-indigo-600 px-4 py-2 rounded-lg text-sm font-bold min-h-[44px]">
              Bildirimlere İzin Ver
            </button>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50 rounded-t-lg">
          <h2 className="font-bold text-lg text-gray-800">Kurallar</h2>
          <button 
            disabled={!isOnline}
            className={`px-4 py-2 rounded-lg text-sm font-medium min-h-[44px] ${
              isOnline ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Yeni Kural
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
                    Son: {rule.last_triggered_at ? new Date(rule.last_triggered_at).toLocaleString() : "Yok"}
                  </div>
                </div>
                <div>
                  {rule.is_enabled ? (
                    <span className="text-green-600 flex items-center gap-1 text-sm font-semibold">
                      <Bell size={16} /> <span className="hidden md:inline">Aktif</span>
                    </span>
                  ) : (
                    <span className="text-gray-400 flex items-center gap-1 text-sm font-semibold">
                      <BellOff size={16} /> <span className="hidden md:inline">Pasif</span>
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
          <h2 className="font-bold text-lg text-gray-800">Geçmiş Bildirimler</h2>
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
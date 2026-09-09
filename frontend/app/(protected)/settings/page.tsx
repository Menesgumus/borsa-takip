"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchApi } from "@/lib/api";
import { useState, useEffect } from "react";
import { User, Shield, GraduationCap, Save } from "lucide-react";

export default function SettingsPage() {
  const { data: user } = useQuery({
    queryKey: ["auth_me"],
    queryFn: () => fetchApi("/api/v1/auth/me"),
  });

  const [riskTolerance, setRiskTolerance] = useState("MEDIUM");
  const [explanationLevel, setExplanationLevel] = useState("PRO");
  const [saved, setSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    fetchApi("/api/v1/users/profile").then((profile: any) => {
      if (profile?.risk_tolerance) {
        setRiskTolerance(profile.risk_tolerance);
      }
    }).catch(console.error);

    const storedLevel = localStorage.getItem('bt_explanation_level');
    if (storedLevel) setExplanationLevel(storedLevel);
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await fetchApi("/api/v1/users/profile", {
        method: "PUT",
        body: JSON.stringify({
          risk_tolerance: riskTolerance,
        })
      });
      localStorage.setItem('bt_explanation_level', explanationLevel);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) {
      console.error(e);
      alert("Hata oluştu.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-2xl lg:text-3xl font-bold text-navy-900 tracking-tight">Ayarlar</h1>
        <p className="text-navy-700 mt-1">Hesap bilgileri ve uygulama tercihleri.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-1 space-y-2">
          <div className="p-4 bg-slate-100 rounded-xl text-navy-900 font-medium flex items-center gap-2 border border-slate-200">
            <User size={18} /> Profil Bilgileri
          </div>
          <div className="p-4 text-navy-700 font-medium flex items-center gap-2 hover:bg-slate-50 rounded-xl cursor-pointer">
            <Shield size={18} /> Güvenlik ve Risk
          </div>
          <div className="p-4 text-navy-700 font-medium flex items-center gap-2 hover:bg-slate-50 rounded-xl cursor-pointer">
            <GraduationCap size={18} /> Mentor Tercihleri
          </div>
        </div>

        <div className="md:col-span-2 space-y-6">
          <div className="bg-surface rounded-xl p-6 border border-navy-800/10 shadow-sm">
            <h3 className="text-lg font-bold text-navy-900 mb-4 border-b pb-2">Hesap Bilgileri</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-navy-700 mb-1">E-Posta Adresi</label>
                <input 
                  type="email" 
                  disabled 
                  value={(user as any)?.email || ''} 
                  className="w-full px-4 py-2 border border-slate-200 rounded-lg bg-slate-50 text-slate-500"
                />
              </div>
            </div>
          </div>

          <div className="bg-surface rounded-xl p-6 border border-navy-800/10 shadow-sm">
            <h3 className="text-lg font-bold text-navy-900 mb-4 border-b pb-2">Risk Tercihleri</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-navy-700 mb-1">Risk Toleransı</label>
                <select 
                  value={riskTolerance}
                  onChange={e => setRiskTolerance(e.target.value)}
                  className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500"
                >
                  <option value="CONSERVATIVE">Düşük (Muhafazakar)</option>
                  <option value="MODERATE">Orta (Dengeli)</option>
                  <option value="AGGRESSIVE">Yüksek (Agresif)</option>
                </select>
                <p className="text-xs text-slate-500 mt-1">Karar motoru portföy uyumu hesaplarken bu değeri dikkate alacaktır.</p>
              </div>
            </div>
          </div>

          <div className="bg-surface rounded-xl p-6 border border-navy-800/10 shadow-sm">
            <h3 className="text-lg font-bold text-navy-900 mb-4 border-b pb-2">Finansal Mentor</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-navy-700 mb-1">Varsayılan Açıklama Seviyesi</label>
                <select 
                  value={explanationLevel}
                  onChange={e => setExplanationLevel(e.target.value)}
                  className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-500"
                >
                  <option value="BEGINNER">Başlangıç (Eğitim Odaklı)</option>
                  <option value="INTERMEDIATE">Orta Seviye</option>
                  <option value="PRO">Profesyonel (Sadece Veri)</option>
                </select>
                <p className="text-xs text-slate-500 mt-1">Yapay zeka asistanının size nasıl yanıt vereceğini belirler.</p>
              </div>
            </div>
          </div>

          <div className="flex justify-end items-center gap-4">
            {saved && <span className="text-success-600 font-medium text-sm">Değişiklikler kaydedildi!</span>}
            <button 
              onClick={handleSave}
              disabled={isSaving}
              className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save size={18} /> {isSaving ? "Kaydediliyor..." : "Kaydet"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

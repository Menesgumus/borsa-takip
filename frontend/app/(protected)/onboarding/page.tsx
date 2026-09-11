"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { fetchApi } from "@/lib/api";
import { Check, ShieldCheck } from "lucide-react";

export default function OnboardingPage() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [riskTolerance, setRiskTolerance] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const router = useRouter();

  const handleComplete = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!riskTolerance) return; // Form validation guards this anyway
    setLoading(true);
    setErrorMsg(null);

    try {
      await fetchApi("/api/v1/users/profile", {
        method: "PUT",
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          risk_tolerance: riskTolerance,
          onboarding_completed: true
        }),
      });
      window.location.href = "/dashboard";
    } catch (err: any) {
      console.error(err);
      if (err.status === 401) {
        setErrorMsg("Oturumunuz süresi dolmuş. Lütfen tekrar giriş yapın.");
      } else if (err.status === 422) {
        setErrorMsg("Girdiğiniz veriler geçersiz. Lütfen kontrol edip tekrar deneyin.");
      } else if (err.status === 500) {
        setErrorMsg("Sunucu hatası oluştu. Lütfen daha sonra tekrar deneyin.");
      } else if (err.name === 'AbortError' || err.message?.includes('timeout')) {
        setErrorMsg("İstek zaman aşımına uğradı. Tekrar deneyin.");
      } else {
        setErrorMsg("Profil güncellenirken bir hata oluştu. Lütfen tekrar deneyin.");
      }
    } finally {
      setLoading(false);
    }
  };

  const riskOptions = [
    {
      value: "LOW",
      label: "DÜŞÜK",
      desc: "Dalgalanmayı mümkün olduğunca sınırlamak istiyorum."
    },
    {
      value: "MEDIUM",
      label: "ORTA",
      desc: "Getiri ve risk arasında dengeli yaklaşım istiyorum."
    },
    {
      value: "HIGH",
      label: "YÜKSEK",
      desc: "Daha yüksek dalgalanmayı kabul edebilirim."
    }
  ];

  return (
    <div className="max-w-2xl mx-auto py-12 animate-in fade-in duration-500">
      <div className="mb-8 text-center">
        <div className="w-16 h-16 bg-primary-100 text-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <ShieldCheck size={32} />
        </div>
        <h1 className="text-3xl font-bold text-navy-900 mb-2">Profilinizi Tamamlayın</h1>
        <p className="text-slate-500 text-lg">Yatırım deneyiminizi size özel hale getirmemiz için birkaç bilgiye ihtiyacımız var.</p>
      </div>

      <form onSubmit={handleComplete} className="bg-surface rounded-2xl shadow-sm border border-navy-800/10 p-8 space-y-8">
        
        {errorMsg && (
          <div className="p-4 rounded-lg bg-danger-50 text-danger-700 border border-danger-200 text-sm font-medium">
            {errorMsg}
          </div>
        )}

        {/* Ad Soyad */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-semibold text-navy-900 mb-2" htmlFor="firstName">
              Adınız
            </label>
            <input
              id="firstName"
              type="text"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              placeholder="Ahmet"
              className="w-full px-4 py-3 bg-white text-navy-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 font-medium placeholder:text-slate-400"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-navy-900 mb-2" htmlFor="lastName">
              Soyadınız
            </label>
            <input
              id="lastName"
              type="text"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              placeholder="Yılmaz"
              className="w-full px-4 py-3 bg-white text-navy-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 font-medium placeholder:text-slate-400"
              required
            />
          </div>
        </div>

        {/* Risk Profile */}
        <div>
          <label className="block text-sm font-semibold text-navy-900 mb-4">
            Risk Toleransınız
          </label>
          <div className="space-y-3">
            {riskOptions.map((opt) => {
              const isSelected = riskTolerance === opt.value;
              return (
                <label 
                  key={opt.value}
                  className={`relative flex cursor-pointer rounded-xl border p-4 transition-all hover:bg-slate-50 focus-within:ring-2 focus-within:ring-primary-500 ${
                    isSelected 
                      ? 'border-primary-500 bg-primary-50/50' 
                      : 'border-slate-200 bg-white'
                  }`}
                >
                  <input 
                    type="radio" 
                    name="risk_tolerance" 
                    value={opt.value} 
                    className="sr-only" 
                    onChange={() => setRiskTolerance(opt.value)}
                    required
                  />
                  <div className="flex flex-1">
                    <div className="flex flex-col">
                      <span className={`block text-sm font-bold ${isSelected ? 'text-primary-900' : 'text-navy-900'}`}>
                        {opt.label}
                      </span>
                      <span className={`mt-1 flex items-center text-sm ${isSelected ? 'text-primary-700' : 'text-navy-700/80'}`}>
                        {opt.desc}
                      </span>
                    </div>
                  </div>
                  <Check 
                    className={`h-5 w-5 shrink-0 transition-opacity ${isSelected ? 'text-primary-600 opacity-100' : 'opacity-0'}`} 
                  />
                </label>
              );
            })}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || !riskTolerance}
          className="w-full py-4 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-bold text-lg transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Kaydediliyor..." : "Başla"}
        </button>
      </form>
    </div>
  );
}

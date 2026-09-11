"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { fetchApi } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await fetchApi("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      // Force a full reload to clear Next.js client router cache and ensure cookies are sent
      window.location.href = "/dashboard";
    } catch (err: any) {
      setError(err.message || "Giriş başarısız.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main role="main" id="main-content" className="min-h-screen bg-slate-50 flex">
      {/* Left panel - Branding */}
      <aside aria-label="Branding" className="hidden lg:flex lg:w-1/2 bg-navy-900 flex-col justify-between p-12 text-white">
        <div>
          <div className="flex items-center gap-3 font-bold text-2xl tracking-tight mb-8">
            <div className="w-10 h-10 rounded bg-primary-500 flex items-center justify-center text-white">BT</div>
            Borsa Takip
          </div>
          <h2 className="text-4xl font-bold leading-tight mt-20">
            Kişisel yatırım <br/>
            kararlarınızı <span className="text-primary-400">güçlendirin.</span>
          </h2>
          <p className="text-navy-300 mt-6 text-lg max-w-md">
            Piyasa verileri, teknik analizler ve kişisel karar destek araçları ile yatırımlarınızı daha iyi yönetin.
          </p>
        </div>
        <div className="text-sm text-navy-400">
          &copy; {new Date().getFullYear()} Borsa Takip. Tüm hakları saklıdır.
        </div>
      </aside>

      {/* Right panel - Form */}
      <section aria-label="Auth Form" className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-100 p-8 sm:p-10">
          <div className="lg:hidden flex items-center gap-3 font-bold text-2xl tracking-tight mb-8 text-navy-900">
            <div className="w-8 h-8 rounded bg-primary-600 flex items-center justify-center text-white">BT</div>
            Borsa Takip
          </div>

          <h1 className="text-2xl font-bold text-navy-900">Tekrar Hoş Geldiniz</h1>
          <p className="text-slate-500 mt-2 mb-8">Hesabınıza giriş yaparak portföyünüze ulaşın.</p>

          <form onSubmit={handleLogin} className="space-y-5">
            {error && (
              <div className="p-3 bg-danger-50 border border-danger-200 text-danger-700 rounded-lg text-sm font-medium">
                {error}
              </div>
            )}
            
            <div>
              <label className="block text-sm font-semibold text-navy-800 mb-1.5" htmlFor="email">
                E-posta Adresi
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="ornek@sirket.com"
                className="w-full px-4 py-3 bg-white text-navy-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-shadow placeholder:text-slate-400 font-medium"
                required
              />
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="block text-sm font-semibold text-navy-800" htmlFor="password">
                  Şifre
                </label>
              </div>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-3 bg-white text-navy-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-shadow placeholder:text-slate-400 font-medium"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-semibold transition-colors disabled:opacity-70 disabled:cursor-not-allowed mt-2 shadow-sm"
            >
              {loading ? "Giriş Yapılıyor..." : "Giriş Yap"}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-100 text-center">
            <p className="text-slate-600 text-sm">
              Hesabınız yok mu?{" "}
              <Link href="/register" className="font-semibold text-primary-600 hover:text-primary-700">
                Hemen Hesap Oluşturun
              </Link>
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}

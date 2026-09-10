"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, CheckCircle, Circle, Clock } from "lucide-react";
import Link from "next/link";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

const IMAGE_MAP: Record<string, string> = {
  "rsi-nedir": "/education/rsi.png",
  "macd-nedir": "/education/macd.png",
  "bollinger-bantlari": "/education/bollinger.svg",
  "sma-ema-nedir": "/education/moving-average.png",
  "destek-direnc": "/education/support-resistance.png"
};

export default function EducationDetailClient({ slug }: { slug: string }) {
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: modules, isLoading, isError } = useQuery({
    queryKey: ["education-modules"],
    queryFn: async () => {
      const res = await fetch("/api/v1/education/modules");
      if (!res.ok) throw new Error("Failed to fetch modules");
      return res.json();
    }
  });

  const lesson = modules?.flatMap((m: any) => m.lessons).find((l: any) => l.slug === slug);

  const progressMutation = useMutation({
    mutationFn: async ({ id, is_completed }: { id: number, is_completed: boolean }) => {
      const res = await fetch(`/api/v1/education/lessons/${id}/progress`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_completed, last_position: "end" })
      });
      if (!res.ok) throw new Error("Failed to update progress");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["education-modules"] });
    }
  });

  // Mark as complete automatically when viewed if not already
  useEffect(() => {
    if (lesson && !lesson.is_completed) {
      progressMutation.mutate({ id: lesson.id, is_completed: true });
    }
  }, [lesson]);

  if (isLoading) return <div className="max-w-4xl mx-auto p-4 text-center text-slate-500">Yükleniyor...</div>;
  if (isError || !lesson) return (
    <div className="max-w-4xl mx-auto p-4">
      <Link href="/education" className="text-primary-600 hover:underline flex items-center gap-2 mb-4">
        <ArrowLeft size={16} /> Bilgi Merkezine Dön
      </Link>
      <div className="bg-red-50 text-red-600 p-6 rounded-xl border border-red-200">
        İçerik bulunamadı.
      </div>
    </div>
  );

  const imageSrc = IMAGE_MAP[lesson.slug] || "/education/support-resistance.png";

  return (
    <div className="max-w-3xl mx-auto p-4 pb-20">
      <Link href="/education" className="inline-flex items-center gap-2 text-slate-500 hover:text-navy-900 transition-colors mb-6 font-medium">
        <ArrowLeft size={18} /> Geri Dön
      </Link>

      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        {/* Hero */}
        <div className="bg-slate-50 p-8 border-b border-slate-200 flex flex-col md:flex-row items-center gap-8">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-4 text-sm font-semibold text-slate-500">
              <span className="flex items-center gap-1"><Clock size={16} /> {lesson.estimated_minutes} dk okuma</span>
              <span>•</span>
              {lesson.is_completed ? (
                 <span className="flex items-center gap-1 text-success-600"><CheckCircle size={16} /> Tamamlandı</span>
              ) : (
                 <span className="flex items-center gap-1 text-slate-400"><Circle size={16} /> Okunuyor</span>
              )}
            </div>
            <h1 className="text-3xl font-bold text-navy-900 mb-3">{lesson.title}</h1>
            <p className="text-lg text-slate-600 leading-relaxed">{lesson.summary}</p>
          </div>
          <div className="w-full md:w-1/3 bg-white p-4 rounded-xl border border-slate-100 shadow-sm flex-shrink-0">
             <img src={imageSrc} alt={lesson.title} className="w-full h-auto object-contain max-h-48" />
             <div className="text-[10px] text-center mt-2 text-slate-400">Kaynak: Wikimedia Commons</div>
          </div>
        </div>

        {/* Content */}
        <div className="p-8 space-y-8">
          <section>
            <h2 className="text-xl font-bold text-navy-900 mb-3 border-l-4 border-primary-500 pl-3">Özetle Nedir?</h2>
            <div className="prose prose-slate max-w-none text-slate-700 leading-relaxed text-lg bg-primary-50 p-6 rounded-xl">
              {lesson.content_beginner}
            </div>
          </section>

          <section>
            <h2 className="text-xl font-bold text-navy-900 mb-3 border-l-4 border-slate-800 pl-3">Nasıl Çalışır ve Nasıl Yorumlanır?</h2>
            <div className="prose prose-slate max-w-none text-slate-700 leading-relaxed">
              {lesson.content_detailed}
            </div>
          </section>

          {["rsi-nedir", "macd-nedir", "bollinger-bantlari", "sma-ema-nedir"].includes(lesson.slug) && (
            <section className="bg-amber-50 p-6 rounded-xl border border-amber-200 mt-8">
              <h3 className="font-bold text-amber-900 mb-2 flex items-center gap-2">
                <span className="text-xl">⚠️</span> Karar vermek için tek başına kullanılır mı?
              </h3>
              <p className="text-amber-800 text-sm leading-relaxed">
                Hiçbir teknik gösterge tek başına %100 doğru sonuç vermez. {lesson.title}, sadece piyasanın mevcut durumunu matematiksel bir formülle yansıtır. Karar verirken her zaman diğer teknik analiz araçları (Trend, Hacim) ve temel analiz (şirket haberleri, bilançolar) ile desteklenmelidir. Borsa Takip sistemi bu yüzden birden fazla sinyali harmanlayarak size sonuç üretir.
              </p>
            </section>
          )}

          <div className="pt-8 mt-8 border-t border-slate-200 flex justify-between items-center">
            <button 
              onClick={() => progressMutation.mutate({ id: lesson.id, is_completed: !lesson.is_completed })}
              className={`px-4 py-2 rounded-lg font-medium text-sm flex items-center gap-2 transition-colors ${
                lesson.is_completed ? 'bg-slate-100 text-slate-600 hover:bg-slate-200' : 'bg-primary-600 text-white hover:bg-primary-700'
              }`}
            >
              {lesson.is_completed ? <><CheckCircle size={18} /> Okundu İşaretini Kaldır</> : <><Circle size={18} /> Okundu Olarak İşaretle</>}
            </button>
            <button 
              onClick={() => router.push("/education")}
              className="text-primary-600 font-bold hover:underline"
            >
              Sonraki Derse Geç →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

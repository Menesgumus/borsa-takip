"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, CheckCircle, Circle, Clock, X, ZoomIn } from "lucide-react";
import Link from "next/link";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { EDUCATION_ASSETS } from "@/lib/educationAssets";

export default function EducationDetailClient({ slug }: { slug: string }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [lightboxOpen, setLightboxOpen] = useState(false);

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

  useEffect(() => {
    if (lesson && !lesson.is_completed) {
      progressMutation.mutate({ id: lesson.id, is_completed: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lesson]);

  if (isLoading) return <div className="max-w-5xl mx-auto p-4 text-center text-slate-500">Yükleniyor...</div>;
  if (isError || !lesson) return (
    <div className="max-w-5xl mx-auto p-4">
      <Link href="/education" className="text-primary-600 hover:underline flex items-center gap-2 mb-4">
        <ArrowLeft size={16} /> Bilgi Merkezine Dön
      </Link>
      <div className="bg-red-50 text-red-600 p-6 rounded-xl border border-red-200">
        İçerik bulunamadı.
      </div>
    </div>
  );

  const asset = EDUCATION_ASSETS[lesson.slug];
  const imageSrc = asset ? asset.src : "/education/support-resistance.png";
  const imageAlt = asset ? asset.alt : lesson.title;

  return (
    <div className="max-w-5xl mx-auto p-4 pb-20">
      <Link href="/education" className="inline-flex items-center gap-2 text-slate-500 hover:text-navy-900 transition-colors mb-6 font-medium">
        <ArrowLeft size={18} /> Geri Dön
      </Link>

      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        {/* Title Header */}
        <div className="bg-slate-50 p-8 border-b border-slate-200">
          <div className="flex items-center gap-3 mb-4 text-sm font-semibold text-slate-500">
            <span className="flex items-center gap-1"><Clock size={16} /> {lesson.estimated_minutes} dk okuma</span>
            <span>•</span>
            {lesson.is_completed ? (
               <span className="flex items-center gap-1 text-success-600"><CheckCircle size={16} /> Tamamlandı</span>
            ) : (
               <span className="flex items-center gap-1 text-slate-400"><Circle size={16} /> Okunuyor</span>
            )}
          </div>
          <h1 className="text-4xl font-bold text-navy-900 mb-4">{lesson.title}</h1>
          <p className="text-xl text-slate-600 leading-relaxed max-w-3xl">{lesson.summary}</p>
        </div>

        {/* Large Figure */}
        <div className="bg-white p-6 md:p-10 border-b border-slate-100 flex flex-col items-center">
           <div 
             className="relative w-full max-w-4xl cursor-zoom-in group rounded-xl overflow-hidden bg-slate-50 border border-slate-200 flex items-center justify-center p-4 md:p-8"
             onClick={() => setLightboxOpen(true)}
             title="Büyütmek için tıkla"
           >
             <img 
               src={imageSrc} 
               alt={imageAlt} 
               className="w-full h-auto object-contain max-h-[500px]" 
             />
             <div className="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors flex items-center justify-center">
               <div className="bg-white/90 backdrop-blur text-navy-900 px-4 py-2 rounded-full font-bold shadow-lg opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-2">
                 <ZoomIn size={18} /> Resmi Büyüt
               </div>
             </div>
           </div>
           <div className="text-xs text-center mt-3 text-slate-400 font-medium">
             Kaynak: {asset?.sourceLabel || "Wikimedia Commons"}
           </div>
        </div>

        {/* Content */}
        <div className="p-8 md:p-12 space-y-10 max-w-4xl mx-auto">
          <section>
            <h2 className="text-2xl font-bold text-navy-900 mb-4 border-l-4 border-primary-500 pl-4">Özetle Nedir?</h2>
            <div className="prose prose-slate max-w-none text-slate-700 leading-relaxed text-lg bg-primary-50 p-6 md:p-8 rounded-xl">
              {lesson.content_beginner}
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-navy-900 mb-4 border-l-4 border-slate-800 pl-4">Nasıl Çalışır ve Nasıl Yorumlanır?</h2>
            <div className="prose prose-slate max-w-none text-slate-700 leading-relaxed text-lg">
              {lesson.content_detailed}
            </div>
          </section>

          {["rsi-nedir", "macd-nedir", "bollinger-bantlari", "sma-ema-nedir"].includes(lesson.slug) && (
            <section className="bg-amber-50 p-6 md:p-8 rounded-xl border border-amber-200 mt-8">
              <h3 className="text-xl font-bold text-amber-900 mb-3 flex items-center gap-2">
                <span>💡</span> Karar vermek için tek başına kullanılır mı?
              </h3>
              <p className="text-amber-800 text-base md:text-lg leading-relaxed">
                Hiçbir teknik gösterge tek başına %100 doğru sonuç vermez. {lesson.title}, sadece piyasanın mevcut durumunu matematiksel bir formülle yansıtır. Karar verirken her zaman diğer teknik analiz araçları (Trend, Hacim) ve temel analiz (Şirket haberleri, bilançolar) ile desteklenmelidir.
              </p>
            </section>
          )}

          <div className="pt-8 mt-12 border-t border-slate-200 flex justify-between items-center">
            <button 
              onClick={() => progressMutation.mutate({ id: lesson.id, is_completed: !lesson.is_completed })}
              className={`px-5 py-3 rounded-lg font-bold text-sm flex items-center gap-2 transition-colors ${
                lesson.is_completed ? 'bg-slate-100 text-slate-600 hover:bg-slate-200' : 'bg-primary-600 text-white hover:bg-primary-700'
              }`}
            >
              {lesson.is_completed ? <><CheckCircle size={20} /> Okundu İşaretini Kaldır</> : <><Circle size={20} /> Okundu Olarak İşaretle</>}
            </button>
            <button 
              onClick={() => router.push("/education")}
              className="text-primary-600 font-bold hover:underline flex items-center gap-1 text-lg"
            >
              Sonraki Derse Geç <span>→</span>
            </button>
          </div>
        </div>
      </div>

      {/* Lightbox Modal */}
      {lightboxOpen && (
        <div 
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-sm p-4 md:p-8 animate-in fade-in duration-200"
          onClick={() => setLightboxOpen(false)}
        >
          <button 
            className="absolute top-6 right-6 text-white/70 hover:text-white bg-white/10 hover:bg-white/20 p-2 rounded-full transition-colors"
            onClick={(e) => { e.stopPropagation(); setLightboxOpen(false); }}
          >
            <X size={24} />
          </button>
          <img 
            src={imageSrc} 
            alt={imageAlt} 
            className="w-full h-full object-contain max-w-[95vw] max-h-[90vh]" 
            onClick={(e) => e.stopPropagation()} 
          />
        </div>
      )}
    </div>
  );
}

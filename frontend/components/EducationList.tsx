"use client";

import { useQuery } from "@tanstack/react-query";
import { CheckCircle, Circle, BookOpen, Clock } from "lucide-react";
import Link from "next/link";
import Image from "next/image";

import { EDUCATION_ASSETS } from "@/lib/educationAssets";

const CATEGORY_LABELS: Record<string, string> = {
  "TECHNICAL_ANALYSIS": "Teknik Analiz",
  "FUNDAMENTALS": "Temel Analiz",
  "PORTFOLIO": "Portföy ve Risk"
};

export function EducationList() {
  const { data: modules, isLoading, isError } = useQuery({
    queryKey: ["education-modules"],
    queryFn: async () => {
      const res = await fetch("/api/v1/education/modules");
      if (!res.ok) throw new Error("Failed to fetch modules");
      return res.json();
    }
  });

  if (isLoading) return <div className="text-center p-12 text-slate-500">Yükleniyor...</div>;
  if (isError) return <div className="bg-red-50 text-red-600 p-6 rounded-xl border border-red-200">Eğitim modülleri yüklenirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.</div>;
  if (!modules || modules.length === 0) return <div className="text-center p-12 bg-white rounded-xl border border-gray-200 text-slate-500">Henüz eğitim modülü bulunmuyor.</div>;

  return (
    <div className="space-y-12">
      {modules.map((m: any) => (
        <div key={m.id}>
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-navy-900">{m.title}</h2>
            {m.description && <p className="text-slate-600 mt-1">{m.description}</p>}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {m.lessons.map((lesson: any) => {
              const asset = EDUCATION_ASSETS[lesson.slug];
              const imageSrc = asset ? asset.src : "/education/placeholder.svg"; // Safest fallback
              return (
                <Link key={lesson.id} href={`/education/${lesson.slug}`} className="flex flex-col bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow overflow-hidden group">
                  {/* Image Thumbnail */}
                  <div className="relative h-[200px] bg-slate-50 flex items-center justify-center border-b border-slate-100 overflow-hidden">
                    <img 
                      src={imageSrc} 
                      alt={asset ? asset.alt : lesson.title} 
                      className="w-full h-full object-contain p-6 group-hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-3 right-3 bg-white/90 backdrop-blur text-xs font-bold px-2 py-1 rounded shadow-sm text-navy-800">
                      {CATEGORY_LABELS[m.category] || m.category}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-5 flex flex-col flex-1">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <h3 className="font-bold text-lg text-navy-900 leading-tight group-hover:text-primary-600 transition-colors">
                        {lesson.title}
                      </h3>
                      {lesson.is_completed ? (
                        <CheckCircle className="text-success-500 shrink-0 w-5 h-5" />
                      ) : (
                        <Circle className="text-slate-300 shrink-0 w-5 h-5" />
                      )}
                    </div>
                    
                    <p className="text-sm text-slate-600 mb-4 line-clamp-2 flex-1">
                      {lesson.summary}
                    </p>

                    <div className="flex items-center justify-between mt-auto pt-4 border-t border-slate-100">
                      <div className="flex items-center gap-1.5 text-xs font-medium text-slate-500">
                        <Clock className="w-4 h-4" />
                        <span>{lesson.estimated_minutes} dk</span>
                      </div>
                      <span className="text-primary-600 font-semibold text-sm flex items-center gap-1 group-hover:gap-2 transition-all">
                        {lesson.is_completed ? "Tekrar İncele" : "Oku"} <span>→</span>
                      </span>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

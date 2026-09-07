"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle, Circle, BookOpen, Clock } from "lucide-react";
import { useState } from "react";

export function EducationList() {
  const queryClient = useQueryClient();
  const [activeLesson, setActiveLesson] = useState<any | null>(null);
  const [level, setLevel] = useState<"BEGINNER"|"DETAILED">("BEGINNER");

  const { data: modules, isLoading } = useQuery({
    queryKey: ["education-modules"],
    queryFn: async () => {
      const res = await fetch("/api/v1/education/modules");
      if (!res.ok) throw new Error("Failed to fetch modules");
      return res.json();
    }
  });

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

  if (isLoading) return <div>Yükleniyor...</div>;

  if (activeLesson) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <button onClick={() => setActiveLesson(null)} className="text-blue-600 mb-4 hover:underline">&larr; Geri Dön</button>
        
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-bold">{activeLesson.title}</h2>
            <p className="text-gray-500 mt-1">{activeLesson.summary}</p>
          </div>
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button 
              onClick={() => setLevel("BEGINNER")}
              className={`px-3 py-1 rounded text-sm ${level === "BEGINNER" ? "bg-white shadow-sm font-bold" : "text-gray-500"}`}
            >
              Basit Anlatım
            </button>
            <button 
              onClick={() => setLevel("DETAILED")}
              className={`px-3 py-1 rounded text-sm ${level === "DETAILED" ? "bg-white shadow-sm font-bold" : "text-gray-500"}`}
            >
              Detaylı Anlatım
            </button>
          </div>
        </div>

        <div className="prose max-w-none text-gray-800 mb-8 border-l-4 border-blue-500 pl-4 py-2 bg-blue-50 rounded-r-lg">
          {level === "BEGINNER" ? activeLesson.content_beginner : activeLesson.content_detailed}
        </div>

        {activeLesson.key_points && (
          <div className="mb-8">
            <h3 className="font-bold mb-2">Önemli Noktalar</h3>
            <div className="flex flex-wrap gap-2">
              {activeLesson.key_points.split(",").map((kp: string, i: number) => (
                <span key={i} className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">{kp.trim()}</span>
              ))}
            </div>
          </div>
        )}

        <div className="border-t border-gray-200 pt-6 flex justify-end">
          <button
            onClick={() => progressMutation.mutate({ id: activeLesson.id, is_completed: !activeLesson.is_completed })}
            className={`flex items-center gap-2 px-6 py-2 rounded-lg font-bold text-white transition-colors ${
              activeLesson.is_completed ? "bg-green-600 hover:bg-green-700" : "bg-blue-600 hover:bg-blue-700"
            }`}
          >
            {activeLesson.is_completed ? <CheckCircle /> : <Circle />}
            {activeLesson.is_completed ? "Tamamlandı Olarak İşaretli" : "Tamamlandı İşaretle"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {modules?.map((mod: any) => (
        <div key={mod.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="bg-gray-50 p-4 border-b border-gray-200">
            <h2 className="font-bold text-lg text-gray-800">{mod.title}</h2>
            <p className="text-sm text-gray-500">{mod.description}</p>
          </div>
          <div className="divide-y divide-gray-100">
            {mod.lessons.map((lesson: any) => (
              <div 
                key={lesson.id} 
                className="p-4 flex items-center justify-between hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => { setActiveLesson(lesson); setLevel("BEGINNER"); }}
              >
                <div className="flex items-center gap-4">
                  <div className={`${lesson.is_completed ? "text-green-500" : "text-gray-300"}`}>
                    {lesson.is_completed ? <CheckCircle size={24} /> : <Circle size={24} />}
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-800">{lesson.title}</h3>
                    <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                      <span className="flex items-center gap-1"><Clock size={12} /> {lesson.estimated_minutes} dk</span>
                      {lesson.related_terms && <span className="flex items-center gap-1"><BookOpen size={12} /> {lesson.related_terms}</span>}
                    </div>
                  </div>
                </div>
                <button className="text-blue-600 font-semibold text-sm">Oku</button>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

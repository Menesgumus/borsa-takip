"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Send, Brain, AlertTriangle, ShieldCheck, User as UserIcon } from "lucide-react";

export default function MentorChat({ symbol, threadId }: { symbol: string, threadId?: number }) {
  const [input, setInput] = useState("");
  const [level, setLevel] = useState("BEGINNER");
  const queryClient = useQueryClient();

  const { data: thread } = useQuery({
    queryKey: ["mentor-thread", threadId],
    queryFn: async () => {
      if (!threadId) return null;
      const res = await fetch(`/api/v1/chat/threads/${threadId}`);
      if (!res.ok) throw new Error("Failed");
      return res.json();
    },
    enabled: !!threadId,
  });

  const chatMutation = useMutation({
    mutationFn: async (text: string) => {
      // In a real app we'd create the thread if it doesn't exist yet, but for now we assume threadId exists or we use a temporary mock
      const targetThreadId = threadId || 1; // Fallback
      const res = await fetch(`/api/v1/chat/threads/${targetThreadId}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: text,
          instrument_symbol: symbol,
          explanation_level: level
        })
      });
      if (!res.ok) throw new Error("Chat failed");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mentor-thread", threadId] });
      setInput("");
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    chatMutation.mutate(input);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col h-[500px]">
      <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50 rounded-t-lg">
        <h3 className="font-bold flex items-center gap-2">
          <Brain className="text-blue-600" /> AI Mentor
        </h3>
        <select 
          value={level} 
          onChange={e => setLevel(e.target.value)}
          className="text-sm border border-gray-300 rounded p-1"
        >
          <option value="BEGINNER">Basit Dille (Acemi)</option>
          <option value="PRO">Teknik Dille (Pro)</option>
        </select>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {thread?.messages?.length === 0 && (
          <div className="text-center text-gray-500 mt-10">
            {symbol} hakkında ne öğrenmek istersiniz?
          </div>
        )}
        
        {thread?.messages?.map((msg: any) => {
          if (msg.role === "user") {
            return (
              <div key={msg.id} className="flex justify-end">
                <div className="bg-blue-600 text-white rounded-lg py-2 px-4 max-w-[80%]">
                  {msg.content}
                </div>
              </div>
            );
          }
          
          // Assistant message (Structured JSON)
          let parsed;
          try {
            parsed = JSON.parse(msg.content);
          } catch {
            parsed = { summary: msg.content };
          }

          return (
            <div key={msg.id} className="flex justify-start">
              <div className="bg-gray-100 rounded-lg py-3 px-4 max-w-[90%] text-gray-800">
                <div className="flex items-center gap-2 mb-2 pb-2 border-b border-gray-200">
                  <Brain size={16} className="text-blue-500" />
                  <span className="text-xs font-bold text-gray-500 uppercase">AI Mentor</span>
                  {parsed.synthetic && (
                    <span className="bg-yellow-200 text-yellow-800 text-[10px] px-1 rounded flex items-center gap-1">
                      <ShieldCheck size={10} /> MOCK / GÜVENLİ MOD
                    </span>
                  )}
                </div>
                
                <p className="font-medium mb-2">{parsed.summary}</p>
                
                {parsed.action && (
                  <div className="my-3 bg-white p-2 rounded border border-gray-200 flex items-center gap-2">
                    <span className="text-xs text-gray-500">Motor Kararı:</span>
                    <span className="font-bold text-sm bg-gray-100 px-2 py-0.5 rounded">{parsed.action}</span>
                  </div>
                )}
                
                {parsed.action_explanation && (
                  <p className="text-sm text-gray-600 mb-2">{parsed.action_explanation}</p>
                )}
                
                {parsed.key_reasons?.length > 0 && (
                  <div className="mt-2">
                    <span className="text-xs font-bold text-gray-500">NEDENLER:</span>
                    <ul className="list-disc pl-4 text-sm mt-1">
                      {parsed.key_reasons.map((r: string, i: number) => <li key={i}>{r}</li>)}
                    </ul>
                  </div>
                )}
                
                {parsed.risks?.length > 0 && (
                  <div className="mt-3 bg-red-50 p-2 rounded border border-red-100">
                    <span className="text-xs font-bold text-red-800 flex items-center gap-1">
                      <AlertTriangle size={12} /> RİSKLER:
                    </span>
                    <ul className="list-disc pl-4 text-sm mt-1 text-red-700">
                      {parsed.risks.map((r: string, i: number) => <li key={i}>{r}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          );
        })}
        {chatMutation.isPending && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg py-3 px-4 text-gray-500 text-sm animate-pulse">
              Düşünüyor...
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-gray-200">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Sorunuzu yazın..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={chatMutation.isPending}
          />
          <button 
            type="submit" 
            disabled={chatMutation.isPending || !input.trim()}
            className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";
import { Send, User, Bot, Sparkles, GraduationCap } from "lucide-react";
import { fetchApi } from "@/lib/api";

export default function MentorPage() {
  const [messages, setMessages] = useState<{role: string, content: string}[]>([
    {
      role: 'assistant',
      content: 'Merhaba! Ben Borsa Takip finansal asistanınız. Yatırımlarınız, piyasalar veya finansal kavramlar hakkında size nasıl yardımcı olabilirim?'
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"BEGINNER" | "PRO">("BEGINNER");

  const suggestions = [
    "THYAO neden BEKLE veriyor?",
    "Portföyümde en büyük risk ne?",
    "Bugünkü fırsatları açıkla.",
    "RSI (Göreceli Güç Endeksi) nedir?"
  ];

  const handleSend = async (text: string) => {
    if (!text.trim()) return;
    
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      // Fake delay for UI since the mentor backend endpoint is context-aware and might take time
      const data = await fetchApi('/api/v1/mentor/chat', {
        method: 'POST',
        body: JSON.stringify({ message: text, context_symbol: null })
      });
      
      setMessages(prev => [...prev, { role: 'assistant', content: (data as any).reply || "Bir yanıt oluşturamadım." }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Bağlantı hatası oluştu. Lütfen tekrar deneyin." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col animate-in fade-in duration-500">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-navy-900 tracking-tight flex items-center gap-2">
            <Sparkles className="text-primary-600" /> Finansal Mentor
          </h1>
          <p className="text-navy-700 mt-1">Yapay zeka destekli kişisel yatırım danışmanınız.</p>
        </div>
        
        {/* Beginner / Pro Toggle */}
        <div className="bg-slate-100 p-1 rounded-lg flex text-sm font-medium">
          <button 
            onClick={() => setMode("BEGINNER")}
            className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-colors ${mode === "BEGINNER" ? "bg-white text-primary-600 shadow-sm" : "text-slate-500"}`}
          >
            <GraduationCap size={16} /> Başlangıç
          </button>
          <button 
            onClick={() => setMode("PRO")}
            className={`px-3 py-1.5 rounded-md transition-colors ${mode === "PRO" ? "bg-white text-primary-600 shadow-sm" : "text-slate-500"}`}
          >
            PRO
          </button>
        </div>
      </div>

      <div className="flex-1 bg-surface rounded-2xl border border-navy-800/10 shadow-sm flex flex-col overflow-hidden">
        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/50">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-4 max-w-[85%] ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                msg.role === 'user' ? 'bg-navy-900 text-white' : 'bg-primary-100 text-primary-700'
              }`}>
                {msg.role === 'user' ? <User size={16} /> : <Bot size={18} />}
              </div>
              <div className={`p-4 rounded-2xl text-sm ${
                msg.role === 'user' 
                  ? 'bg-primary-600 text-white rounded-tr-sm' 
                  : 'bg-white border border-slate-200 text-navy-900 rounded-tl-sm shadow-sm'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-4 max-w-[85%]">
              <div className="w-8 h-8 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center shrink-0">
                <Bot size={18} />
              </div>
              <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm rounded-tl-sm flex gap-1">
                <span className="w-2 h-2 rounded-full bg-slate-300 animate-bounce"></span>
                <span className="w-2 h-2 rounded-full bg-slate-300 animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                <span className="w-2 h-2 rounded-full bg-slate-300 animate-bounce" style={{ animationDelay: '0.4s' }}></span>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white border-t border-slate-100">
          {messages.length < 3 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {suggestions.map((sug, i) => (
                <button 
                  key={i} 
                  onClick={() => handleSend(sug)}
                  className="px-3 py-1.5 bg-primary-50 text-primary-700 hover:bg-primary-100 border border-primary-100 rounded-full text-xs font-medium transition-colors"
                >
                  {sug}
                </button>
              ))}
            </div>
          )}
          
          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(input); }}
            className="flex gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Mentor'a sor..."
              className="flex-1 px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:bg-white transition-all text-sm"
              disabled={loading}
            />
            <button 
              type="submit"
              disabled={!input.trim() || loading}
              className="px-4 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

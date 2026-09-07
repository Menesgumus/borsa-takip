"use client";

import { useState } from "react";
import { Send, BrainCircuit, ShieldAlert, WifiOff } from "lucide-react";
import { useNetwork } from "@/components/NetworkProvider";

export default function MentorPage() {
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);
  const [input, setInput] = useState("");
  const { isOnline } = useNetwork();

  const handleSend = () => {
    if (!input.trim() || !isOnline) return;
    
    // Add user message
    const newMessages = [...messages, { role: "user", content: input }];
    setMessages(newMessages);
    setInput("");

    // Mock AI response
    setTimeout(() => {
      setMessages([...newMessages, { 
        role: "assistant", 
        content: "Yapay zeka asistanı şu an test modundadır." 
      }]);
    }, 1000);
  };

  return (
    <div className="max-w-4xl mx-auto h-[80vh] flex flex-col p-4">
      <div className="mb-4">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <BrainCircuit className="text-purple-600" /> AI Mentor
        </h1>
        <p className="text-gray-600">Portföyünüz ve piyasa hakkında sorular sorun.</p>
      </div>

      {!isOnline && (
        <div className="bg-gray-800 border-l-4 border-yellow-500 text-yellow-100 p-4 mb-6 shadow-sm relative z-0">
          <h3 className="font-bold mb-1">Cihazınız Çevrimdışı (STALE DATA)</h3>
          <p className="text-sm">
            AI Mentor canlı bağlantı gerektirir. Lütfen internet bağlantınızı kontrol edip tekrar deneyin.
          </p>
        </div>
      )}

      <div className="flex-1 bg-white rounded-lg shadow-sm border border-gray-200 overflow-y-auto p-4 space-y-4 mb-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-20">
            AI Mentor&apos;e bir soru sorarak başlayın.
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg ${
              m.role === 'user' ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-gray-100 text-gray-800 rounded-bl-none'
            }`}>
              {m.content}
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder={isOnline ? "Mentore danışın..." : "Çevrimdışıyken mesaj gönderilemez"}
          disabled={!isOnline}
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2 disabled:bg-gray-100 disabled:cursor-not-allowed text-base"
        />
        <button 
          onClick={handleSend}
          disabled={!isOnline || !input.trim()}
          className="bg-indigo-600 text-white px-6 py-2 rounded-lg disabled:opacity-50 min-w-[44px] min-h-[44px] flex items-center justify-center"
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
}

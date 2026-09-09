"use client";

import { useState, useEffect, useRef } from "react";
import { Send, User, Bot, Sparkles, GraduationCap, Plus, AlertCircle } from "lucide-react";
import { fetchApi } from "@/lib/api";

interface ParsedMentorResponse {
  response_kind?: string;
  summary: string;
  action_explanation: string;
  key_reasons: string[];
  risks: string[];
  data_quality_note?: string | null;
  learning_points: string[];
  action: string;
  synthetic: boolean;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  parsed?: ParsedMentorResponse;
  error?: boolean;
}

const ACTION_LABEL: Record<string, string> = {
  STRONG_BUY: "AL",
  BUY: "KADEMELİ AL",
  HOLD: "BEKLE",
  SELL: "KADEMELİ SAT",
  STRONG_SELL: "SAT",
};

const ACTION_COLOR: Record<string, string> = {
  STRONG_BUY: "text-success-700 bg-success-50 border-success-200",
  BUY: "text-success-600 bg-success-50 border-success-200",
  HOLD: "text-amber-700 bg-amber-50 border-amber-200",
  SELL: "text-orange-600 bg-orange-50 border-orange-200",
  STRONG_SELL: "text-danger-700 bg-danger-50 border-danger-200",
};

function AssistantBubble({ msg }: { msg: Message }) {
  if (msg.error) {
    return (
      <div className="flex gap-3 items-start">
        <div className="w-8 h-8 rounded-full bg-danger-100 flex-shrink-0 flex items-center justify-center">
          <AlertCircle className="text-danger-600" size={16} />
        </div>
        <div className="bg-danger-50 border border-danger-200 rounded-xl px-4 py-3 text-sm text-danger-800">
          {msg.content}
        </div>
      </div>
    );
  }

  if (msg.parsed) {
    const p = msg.parsed;
    const actionLabel = p.action ? ACTION_LABEL[p.action] || p.action : null;
    const actionColor = p.action ? ACTION_COLOR[p.action] || "text-slate-700 bg-slate-50 border-slate-200" : "";

    return (
      <div className="flex gap-3 items-start">
        <div className="w-8 h-8 rounded-full bg-primary-100 flex-shrink-0 flex items-center justify-center">
          <Bot className="text-primary-600" size={16} />
        </div>
        <div className="space-y-3 max-w-[85%]">
          {/* Action badge */}
          {p.action && (
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border ${actionColor}`}>
              {actionLabel}
            </span>
          )}

          {/* Summary */}
          <div className="bg-surface border border-navy-800/10 rounded-xl px-4 py-3 text-sm text-navy-800 leading-relaxed whitespace-pre-wrap">
            {p.summary}
          </div>

          {/* Action explanation */}
          {p.action_explanation && (
            <div className="bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-700 leading-relaxed">
              {p.action_explanation}
            </div>
          )}

          {/* Key reasons */}
          {p.key_reasons && p.key_reasons.length > 0 && (
            <div className="bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 space-y-1">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Nedenler</p>
              {p.key_reasons.map((r, i) => (
                <div key={i} className="text-sm text-navy-800 flex items-start gap-2">
                  <span className="text-primary-500 mt-0.5">•</span> {r}
                </div>
              ))}
            </div>
          )}

          {/* Risks */}
          {p.risks && p.risks.length > 0 && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3 space-y-1">
              <p className="text-xs font-semibold text-amber-600 uppercase tracking-wider mb-2">Riskler</p>
              {p.risks.map((r, i) => (
                <div key={i} className="text-sm text-amber-800 flex items-start gap-2">
                  <span className="mt-0.5">⚠</span> {r}
                </div>
              ))}
            </div>
          )}

          {/* Data quality note */}
          {p.data_quality_note && (
            <div className="bg-slate-100 border border-slate-200 rounded-xl px-4 py-2 text-xs text-slate-500">
              {p.data_quality_note}
            </div>
          )}

          {/* Synthetic badge */}
          {p.synthetic && (
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <GraduationCap size={12} /> Deterministik yanıt
            </span>
          )}
        </div>
      </div>
    );
  }

  // Plain text fallback
  return (
    <div className="flex gap-3 items-start">
      <div className="w-8 h-8 rounded-full bg-primary-100 flex-shrink-0 flex items-center justify-center">
        <Bot className="text-primary-600" size={16} />
      </div>
      <div className="bg-surface border border-navy-800/10 rounded-xl px-4 py-3 text-sm text-navy-800 max-w-[85%] whitespace-pre-wrap leading-relaxed">
        {msg.content}
      </div>
    </div>
  );
}

const SUGGESTIONS = [
  "THYAO neden BEKLE veriyor?",
  "RSI nedir?",
  "MACD nasıl yorumlanır?",
  "Portföy diversifikasyonu nedir?",
];

export default function MentorPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Merhaba! Ben Borsa Takip finansal asistanınız. Yatırımlarınız, teknik göstergeler veya belirli hisseler hakkında sorularınızı yanıtlayabilirim.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"BEGINNER" | "PRO">("BEGINNER");
  const [threadId, setThreadId] = useState<number | null>(null);
  const [initError, setInitError] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [activeSymbol, setActiveSymbol] = useState<string | null>(null);

  const initThread = async () => {
    try {
      setInitError(false);
      const data: any = await fetchApi("/api/v1/chat/threads", {
        method: "POST",
        body: JSON.stringify({ title: "Yeni Sohbet" }),
      });
      setThreadId(data.id);
    } catch (e) {
      console.error(e);
      setInitError(true);
    }
  };

  useEffect(() => {
    initThread();
  }, []);

  useEffect(() => {
    if (messages.length > 1 && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSend = async (text: string) => {
    if (!text.trim() || !threadId) return;

    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    // Active instrument context
    let instrument_symbol = activeSymbol;
    const match = text.match(/\b([A-Z]{4,5})\b/);
    if (match) {
      instrument_symbol = match[1];
      setActiveSymbol(instrument_symbol);
    }

    try {
      const data: any = await fetchApi(`/api/v1/chat/threads/${threadId}/messages`, {
        method: "POST",
        body: JSON.stringify({
          content: text,
          instrument_symbol,
          explanation_level: mode,
        }),
      });

      let parsed: ParsedMentorResponse | undefined;
      let displayContent = data.content;

      try {
        const raw = JSON.parse(displayContent);
        if (raw.summary) {
          parsed = raw as ParsedMentorResponse;
          displayContent = raw.summary;
        }
      } catch {
        // plain string
      }

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: displayContent, parsed },
      ]);
    } catch (e: any) {
      console.error(e);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Bir hata oluştu. Lütfen tekrar deneyin.", error: true },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend(input);
    }
  };

  const lastMessage = messages[messages.length - 1];
  const isLastDecision = lastMessage?.role === 'assistant' && lastMessage?.parsed?.response_kind === 'DECISION';
  const currentSuggestions = isLastDecision ? [
    "RSI bu kararı nasıl etkiliyor?",
    "MACD ne söylüyor?",
    "Temel riskler neler?",
    "Veri kalitesi yeterli mi?"
  ] : [
    "THYAO neden BEKLE veriyor?",
    "RSI nedir?",
    "MACD nasıl yorumlanır?",
    "Portföy çeşitlendirmesi nedir?"
  ];

  const startNewConversation = () => {
    setMessages([
      {
        role: "assistant",
        content:
          "Yeni sohbet başlatıldı. Size nasıl yardımcı olabilirim?",
      },
    ]);
    setThreadId(null);
    initThread();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend(input);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)] max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold text-navy-900 flex items-center gap-2">
            <Sparkles className="text-primary-500" size={22} /> Finansal Mentor
          </h1>
          <p className="text-sm text-navy-700 mt-0.5">
            Deterministik karar motoru + eğitim modu
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-100 rounded-lg p-1">
            <button
              onClick={() => setMode("BEGINNER")}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                mode === "BEGINNER"
                  ? "bg-white text-navy-900 shadow-sm"
                  : "text-slate-500 hover:text-navy-700"
              }`}
            >
              Başlangıç
            </button>
            <button
              onClick={() => setMode("PRO")}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                mode === "PRO"
                  ? "bg-white text-navy-900 shadow-sm"
                  : "text-slate-500 hover:text-navy-700"
              }`}
            >
              Pro
            </button>
          </div>
          <button
            onClick={startNewConversation}
            className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
          >
            <Plus size={15} /> Yeni Sohbet
          </button>
        </div>
      </div>

      {initError && (
        <div className="mb-3 flex items-center gap-2 text-sm text-danger-600 bg-danger-50 border border-danger-200 rounded-lg px-4 py-2">
          <AlertCircle size={14} />
          Sohbet başlatılamadı.{" "}
          <button onClick={initThread} className="underline font-medium">
            Tekrar dene
          </button>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4 pr-1">
        {messages.map((msg, i) =>
          msg.role === "user" ? (
            <div key={i} className="flex gap-3 justify-end">
              <div className="bg-primary-600 text-white rounded-xl px-4 py-3 text-sm max-w-[80%] whitespace-pre-wrap">
                {msg.content}
              </div>
              <div className="w-8 h-8 rounded-full bg-navy-100 flex-shrink-0 flex items-center justify-center">
                <User className="text-navy-600" size={16} />
              </div>
            </div>
          ) : (
            <AssistantBubble key={i} msg={msg} />
          )
        )}

        {loading && (
          <div className="flex gap-3 items-start">
            <div className="w-8 h-8 rounded-full bg-primary-100 flex-shrink-0 flex items-center justify-center">
              <Bot className="text-primary-600" size={16} />
            </div>
            <div className="bg-surface border border-navy-800/10 rounded-xl px-4 py-3">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-2 h-2 bg-primary-400 rounded-full animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => handleSend(s)}
              disabled={!threadId || loading}
              className="px-3 py-1.5 text-sm text-navy-700 bg-slate-100 border border-slate-200 rounded-lg hover:bg-slate-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="border-t border-slate-200 pt-4">
        <div className="flex gap-3 items-end">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={2}
            placeholder={threadId ? "Sorunuzu yazın... (Enter gönderir, Shift+Enter yeni satır)" : "Sohbet başlatılıyor..."}
            disabled={!threadId || loading}
            className="flex-1 px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none disabled:bg-slate-50 disabled:cursor-not-allowed"
          />
          <button
            onClick={() => handleSend(input)}
            disabled={!input.trim() || !threadId || loading}
            className="flex-shrink-0 w-11 h-11 flex items-center justify-center rounded-xl bg-primary-600 text-white hover:bg-primary-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Send size={18} />
          </button>
        </div>
        <p className="text-xs text-slate-400 mt-2 text-center">
          Bu yanıtlar yatırım tavsiyesi değildir. Deterministik karar motoru çıktılarıdır.
        </p>
      </div>
    </div>
  );
}

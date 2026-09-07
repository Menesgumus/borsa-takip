import { AlertCircle, AlertTriangle, TrendingUp, TrendingDown, Target, Brain, LineChart, Info } from "lucide-react";

export default function DecisionCard({ decision }: { decision: any }) {
  if (!decision) return null;

  const actionColors: Record<string, string> = {
    "STRONG_BUY": "bg-green-600 text-white",
    "BUY": "bg-green-400 text-white",
    "HOLD": "bg-yellow-400 text-gray-900",
    "SELL": "bg-red-400 text-white",
    "STRONG_SELL": "bg-red-600 text-white",
  };

  const actionLabels: Record<string, string> = {
    "STRONG_BUY": "AL (STRONG BUY)",
    "BUY": "KADEMELİ AL (BUY)",
    "HOLD": "BEKLE (HOLD)",
    "SELL": "KADEMELİ SAT (SELL)",
    "STRONG_SELL": "SAT (STRONG SELL)",
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2 mb-1">
            <Brain className="text-blue-600" /> Deterministik Karar Motoru
          </h2>
          <p className="text-sm text-gray-500">
            Vade: <span className="font-semibold text-gray-700">{decision.horizon}</span> | 
            Motor: {decision.engine_version}
          </p>
        </div>
        <div className={`px-4 py-2 rounded-lg font-bold text-lg shadow-sm ${actionColors[decision.personal_action || decision.market_view] || "bg-gray-200"}`}>
          {actionLabels[decision.personal_action || decision.market_view] || decision.market_view}
        </div>
      </div>

      {decision.missing_data && (
        <div className="bg-yellow-50 border-l-4 border-yellow-500 p-3 mb-6 rounded text-sm text-yellow-800 flex gap-2 items-start">
          <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />
          <div>
            <strong>Veri Eksikliği (Fail-Safe):</strong> Karar motoru yeterli teknik veri olmadığı için güvenli modda BEKLE (HOLD) üretti.
          </div>
        </div>
      )}

      {decision.personal_action && decision.personal_action !== decision.market_view && (
        <div className="bg-blue-50 border-l-4 border-blue-500 p-3 mb-6 rounded text-sm text-blue-800 flex gap-2 items-start">
          <Info size={16} className="mt-0.5 flex-shrink-0" />
          <div>
            <strong>Kişisel Portföy Müdahalesi:</strong> Piyasa görünümü <em>{actionLabels[decision.market_view]}</em> olmasına rağmen, portföy risk/limit kurallarınız gereği karar <em>{actionLabels[decision.personal_action]}</em> olarak güncellendi.
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <ScoreBox label="Teknik Skor" value={decision.technical_score} />
        <ScoreBox label="Temel Skor" value={decision.fundamental_score} />
        <ScoreBox label="Haber/KAP Skoru" value={decision.news_score} />
        <ScoreBox label="Veri Kalitesi" value={decision.data_quality_score} />
      </div>

      <div className="border-t border-gray-100 pt-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Karar Nedenleri & Uyarılar</h3>
        <div className="flex flex-wrap gap-2">
          {decision.reason_codes?.map((code: string, i: number) => (
            <span key={i} className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded border border-gray-200">
              {code}
            </span>
          ))}
          {decision.warnings?.map((warn: string, i: number) => (
            <span key={`w-${i}`} className="bg-red-50 text-red-700 text-xs px-2 py-1 rounded border border-red-200 flex items-center gap-1">
              <AlertCircle size={10} /> {warn}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

function ScoreBox({ label, value }: { label: string, value: string | number | null }) {
  if (value === null || value === undefined) {
    return (
      <div className="bg-gray-50 p-3 rounded border border-gray-100 text-center">
        <div className="text-xs text-gray-500 mb-1">{label}</div>
        <div className="text-sm font-semibold text-gray-400">N/A</div>
      </div>
    );
  }
  
  const numValue = Number(value);
  const color = numValue >= 60 ? "text-green-600" : numValue <= 40 ? "text-red-600" : "text-yellow-600";
  
  return (
    <div className="bg-white p-3 rounded border border-gray-200 text-center shadow-sm">
      <div className="text-xs text-gray-500 mb-1">{label}</div>
      <div className={`text-xl font-bold ${color}`}>
        {numValue.toFixed(1)}
      </div>
    </div>
  );
}

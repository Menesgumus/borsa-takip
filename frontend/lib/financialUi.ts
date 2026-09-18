/**
 * Reusable financial UI tokens, formatters, and categorical colors.
 */

// Formatters
export function formatTry(value: number | string | null | undefined): string {
  if (value === null || value === undefined) return "-";
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "-";
  return new Intl.NumberFormat("tr-TR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num) + " ₺";
}

export function formatPercent(value: number | string | null | undefined): string {
  if (value === null || value === undefined) return "—";
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "—";
  return new Intl.NumberFormat("tr-TR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 2,
  }).format(num) + "%";
}

export function formatQuantity(value: number | string | null | undefined): string {
  if (value === null || value === undefined) return "-";
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "-";
  // Quantities are often whole numbers, but might be fractional in some contexts
  // For Borsa Istanbul, stocks are whole numbers. We will format to 0 decimals unless it has fractions.
  return new Intl.NumberFormat("tr-TR", {
    maximumFractionDigits: 4,
  }).format(num);
}

// Colors
export const CASH_COLOR = "#0ea5e9"; // Stable clear blue/cyan for cash

const CATEGORICAL_PALETTE = [
  "#3b82f6", // blue-500
  "#f97316", // orange-500
  "#10b981", // emerald-500
  "#8b5cf6", // violet-500
  "#06b6d4", // cyan-500
  "#f43f5e", // rose-500
  "#6366f1", // indigo-500
  "#f59e0b", // amber-500
  "#14b8a6", // teal-500
  "#64748b", // slate-500
  "#d946ef", // fuchsia-500
  "#84cc16", // lime-500
];

export function colorForSymbol(symbol: string): string {
  if (!symbol || symbol === "Nakit") return CASH_COLOR;
  
  // Deterministic hash
  let hash = 0;
  for (let i = 0; i < symbol.length; i++) {
    hash = symbol.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % CATEGORICAL_PALETTE.length;
  return CATEGORICAL_PALETTE[index];
}

export function getProfitLossColorClass(value: number | string | null | undefined): string {
  const num = typeof value === "string" ? parseFloat(value) : (value || 0);
  if (num > 0) return "text-emerald-600";
  if (num < 0) return "text-rose-600";
  return "text-slate-600"; // Neutral
}

export const DATA_STATE_CONFIG: Record<string, { label: string, colorClass: string }> = {
  LIVE: { label: "CANLI", colorClass: "bg-emerald-100 text-emerald-800" },
  DELAYED: { label: "GECİKMELİ", colorClass: "bg-amber-100 text-amber-800" },
  EOD: { label: "GÜN SONU", colorClass: "bg-slate-100 text-slate-700" },
  STALE: { label: "GÜNCEL DEĞİL", colorClass: "bg-orange-100 text-orange-800" },
  MOCK: { label: "TEST VERİSİ", colorClass: "bg-purple-100 text-purple-800" },
  UNAVAILABLE: { label: "VERİ YOK", colorClass: "bg-rose-100 text-rose-800" },
};

export function formatActionLabel(action: string | null | undefined, missingData: boolean = false): string {
  if (missingData) return "VERİ YETERSİZ (BEKLE)";
  switch (action) {
    case 'STRONG_BUY': return 'AL';
    case 'BUY': return 'KADEMELİ AL';
    case 'HOLD': return 'BEKLE';
    case 'SELL': return 'KADEMELİ SAT';
    case 'STRONG_SELL': return 'SAT';
    default: return action || 'BİLİNMİYOR';
  }
}

export function getActionColorClass(action: string | null | undefined, missingData: boolean = false): string {
  if (missingData) return 'bg-slate-100 text-slate-700 border-slate-200';
  switch (action) {
    case 'STRONG_BUY': return 'bg-success-100 text-success-800 border-success-200';
    case 'BUY': return 'bg-success-50 text-success-700 border-success-100';
    case 'HOLD': return 'bg-amber-50 text-amber-700 border-amber-100';
    case 'SELL': return 'bg-danger-50 text-danger-700 border-danger-100';
    case 'STRONG_SELL': return 'bg-danger-100 text-danger-800 border-danger-200';
    default: return 'bg-slate-50 text-slate-600 border-slate-100';
  }
}

export function translateSizingState(state: string | null | undefined): string {
  switch (state) {
    case 'OK': return 'Alım Alanı Uygun';
    case 'OVER_LIMIT': return 'Yoğunluk Limiti';
    case 'NO_CASH': return 'Yetersiz Nakit';
    case 'NOT_ACTIONABLE': return 'Ek Alım Önerilmiyor';
    case 'VALUATION_INCOMPLETE': return 'Portföy Değeri Eksik';
    default: return state || '-';
  }
}

export function translateSizingReason(reason: string): string {
  switch (reason) {
    case 'NON_BUY_ACTION': return 'Mevcut karar ek alımı desteklemiyor.';
    case 'PORTFOLIO_CONCENTRATION_LIMIT': return 'Bu hisse portföyünüzde izin verilen yoğunluk sınırına ulaştı.';
    case 'INSUFFICIENT_CASH_FOR_ONE_SHARE': return 'Kullanılabilir nakit en az 1 adet alım için yeterli değil.';
    case 'INSUFFICIENT_CAPACITY_FOR_ONE_SHARE': return 'Risk sınırları içinde en az 1 adetlik ek alım alanı bulunmuyor.';
    case 'DELAYED_MARKET_DATA': return 'Hesaplama gecikmeli piyasa fiyatı kullanılarak yapılmıştır.';
    case 'PORTFOLIO_VALUATION_INCOMPLETE': return 'Portföydeki bazı varlıklar fiyatlanamadığı için güvenilir alım miktarı hesaplanamıyor.';
    default: return reason;
  }
}

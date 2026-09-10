export interface EducationAsset {
  src: string;
  alt: string;
  sourceLabel: string;
}

export const EDUCATION_ASSETS: Record<string, EducationAsset> = {
  "mum-grafik-nedir": {
    src: "/education/candlestick.svg",
    alt: "Mum Grafik Anatomisi",
    sourceLabel: "İllüstrasyon (Temsili)"
  },
  "trend-nedir": {
    src: "/education/trend.svg",
    alt: "Trend Çizgisi",
    sourceLabel: "İllüstrasyon (Temsili)"
  },
  "destek-direnc": {
    src: "/education/support-resistance.png",
    alt: "Destek ve Direnç",
    sourceLabel: "Wikimedia Commons"
  },
  "rsi-nedir": {
    src: "/education/rsi.png",
    alt: "RSI Göstergesi",
    sourceLabel: "Wikimedia Commons"
  },
  "macd-nedir": {
    src: "/education/macd.png",
    alt: "MACD Göstergesi",
    sourceLabel: "Wikimedia Commons"
  },
  "bollinger-bantlari": {
    src: "/education/bollinger.svg",
    alt: "Bollinger Bantları",
    sourceLabel: "Wikimedia Commons"
  },
  "sma-ema-nedir": {
    src: "/education/moving-average.png",
    alt: "Hareketli Ortalamalar",
    sourceLabel: "Wikimedia Commons"
  },
  "cift-tepe-cift-dip": {
    src: "/education/double-top-bottom.svg",
    alt: "Çift Tepe ve Çift Dip",
    sourceLabel: "İllüstrasyon (Temsili)"
  },
  "obo-tobo": {
    src: "/education/head-shoulders.svg",
    alt: "OBO ve TOBO",
    sourceLabel: "İllüstrasyon (Temsili)"
  },
  "fk-nedir": {
    src: "/education/pe-ratio.svg",
    alt: "F/K Oranı",
    sourceLabel: "İllüstrasyon (Temsili)"
  },
  "kap-nedir": {
    src: "/education/kap.svg",
    alt: "KAP (Kamuyu Aydınlatma Platformu)",
    sourceLabel: "İllüstrasyon (Temsili)"
  },
  "cesitlendirme": {
    src: "/education/diversification.svg",
    alt: "Portföy Çeşitlendirmesi",
    sourceLabel: "İllüstrasyon (Temsili)"
  },
  "stop-loss": {
    src: "/education/stop-loss.svg",
    alt: "Stop-Loss (Zarar Kes)",
    sourceLabel: "İllüstrasyon (Temsili)"
  }
};

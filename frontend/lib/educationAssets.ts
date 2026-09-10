export interface EducationAsset {
  src: string;
  alt: string;
  sourceLabel: string;
}

export const EDUCATION_ASSETS: Record<string, EducationAsset> = {
  "mum-grafik-nedir": {
    src: "/education/candlestick.svg",
    alt: "Mum Grafik Anatomisi",
    sourceLabel: "Wikimedia Commons"
  },
  "trend-nedir": {
    src: "/education/trend.svg",
    alt: "Trend Çizgisi",
    sourceLabel: "Wikimedia Commons"
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
    sourceLabel: "Wikimedia Commons"
  },
  "obo-tobo": {
    src: "/education/head-shoulders.svg",
    alt: "OBO ve TOBO",
    sourceLabel: "Wikimedia Commons"
  },
  "f-k-orani": {
    src: "/education/pe-ratio.svg",
    alt: "F/K Oranı",
    sourceLabel: "Wikimedia Commons"
  },
  "kap-nedir": {
    src: "/education/kap.svg",
    alt: "KAP (Kamuyu Aydınlatma Platformu)",
    sourceLabel: "Wikimedia Commons"
  },
  "portfoy-cesitlendirme": {
    src: "/education/diversification.svg",
    alt: "Portföy Çeşitlendirmesi",
    sourceLabel: "Wikimedia Commons"
  },
  "stop-loss": {
    src: "/education/stop-loss.svg",
    alt: "Stop-Loss (Zarar Kes)",
    sourceLabel: "Wikimedia Commons"
  }
};

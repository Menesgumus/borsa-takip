"use client";

import React, { useEffect, useRef } from "react";
import { createChart, ColorType, IChartApi, ISeriesApi, CandlestickSeries, HistogramSeries, LineSeries } from "lightweight-charts";

export interface OHLCVData {
  time: string; // 'YYYY-MM-DD'
  open: number;
  high: number;
  low: number;
  close: number;
  value?: number; // For volume
}

export interface LineData {
  time: string;
  value: number;
}

export interface SRLevelData {
  price: number;
  type: string; // "SUPPORT" or "RESISTANCE"
}

export interface PatternData {
  time: string;
  name: string;
  type: "up" | "down" | "neutral";
}

interface CandlestickChartProps {
  data: OHLCVData[];
  sma?: LineData[];
  ema?: LineData[];
  srLevels?: SRLevelData[];
  patterns?: PatternData[];
  colors?: {
    backgroundColor?: string;
    lineColor?: string;
    textColor?: string;
  };
}

export const CandlestickChart: React.FC<CandlestickChartProps> = ({
  data,
  sma = [],
  ema = [],
  srLevels = [],
  patterns = [],
  colors: {
    backgroundColor = "transparent",
    textColor = "#333",
  } = {},
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const smaSeriesRef = useRef<ISeriesApi<"Line"> | null>(null);
  const emaSeriesRef = useRef<ISeriesApi<"Line"> | null>(null);
  const priceLinesRef = useRef<any[]>([]);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: backgroundColor },
        textColor,
      },
      grid: {
        vertLines: { color: "#e0e3eb" },
        horzLines: { color: "#e0e3eb" },
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderVisible: false,
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
    });
    candleSeriesRef.current = candleSeries as any;

    const smaSeries = chart.addSeries(LineSeries, {
      color: "#2962FF",
      lineWidth: 2,
    });
    smaSeriesRef.current = smaSeries as any;

    const emaSeries = chart.addSeries(LineSeries, {
      color: "#FF6D00",
      lineWidth: 2,
    });
    emaSeriesRef.current = emaSeries as any;

    const volumeSeries = chart.addSeries(HistogramSeries, {
      color: "#26a69a",
      priceFormat: {
        type: "volume",
      },
      priceScaleId: "", // overlay
    });
    volumeSeriesRef.current = volumeSeries as any;
    
    chart.priceScale("").applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [backgroundColor, textColor]);

  useEffect(() => {
    if (candleSeriesRef.current && volumeSeriesRef.current && data.length > 0) {
      const candleData = data.map((d) => ({
        time: d.time,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      }));
      
      const volumeData = data.map((d) => ({
        time: d.time,
        value: d.value || 0,
        color: d.close >= d.open ? "rgba(38, 166, 154, 0.5)" : "rgba(239, 83, 80, 0.5)",
      }));

      candleSeriesRef.current.setData(candleData as any);
      volumeSeriesRef.current.setData(volumeData as any);
      
      // Add pattern markers
      if (patterns.length > 0) {
        const markers: any[] = patterns.map(p => ({
          time: p.time,
          position: p.type === 'up' ? 'belowBar' : (p.type === 'down' ? 'aboveBar' : 'inBar'),
          color: p.type === 'up' ? '#26a69a' : (p.type === 'down' ? '#ef5350' : '#2962FF'),
          shape: p.type === 'up' ? 'arrowUp' : (p.type === 'down' ? 'arrowDown' : 'circle'),
          text: p.name,
        }));
        
        // Lightweight charts markers must be sorted by time ascending
        markers.sort((a, b) => {
            if (a.time < b.time) return -1;
            if (a.time > b.time) return 1;
            return 0;
        });
        
        (candleSeriesRef.current as any).setMarkers(markers);
      } else {
        (candleSeriesRef.current as any).setMarkers([]);
      }
      
      // Manage S/R Price Lines
      // Remove old lines
      priceLinesRef.current.forEach(line => {
        if (candleSeriesRef.current) {
          candleSeriesRef.current.removePriceLine(line);
        }
      });
      priceLinesRef.current = [];
      
      // Add new lines
      srLevels.forEach(sr => {
        if (candleSeriesRef.current) {
          const line = candleSeriesRef.current.createPriceLine({
            price: sr.price,
            color: sr.type === "SUPPORT" ? "rgba(38, 166, 154, 0.8)" : "rgba(239, 83, 80, 0.8)",
            lineWidth: 2,
            lineStyle: 2, // Dashed
            axisLabelVisible: true,
            title: sr.type === "SUPPORT" ? "SUP" : "RES",
          });
          priceLinesRef.current.push(line);
        }
      });
    }

    if (smaSeriesRef.current && sma.length > 0) {
      smaSeriesRef.current.setData(sma as any);
    }
    
    if (emaSeriesRef.current && ema.length > 0) {
      emaSeriesRef.current.setData(ema as any);
    }

  }, [data, sma, ema, patterns, srLevels]);

  return <div ref={chartContainerRef} style={{ width: "100%", position: "relative" }} />;
};

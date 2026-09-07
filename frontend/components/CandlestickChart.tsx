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

interface CandlestickChartProps {
  data: OHLCVData[];
  sma?: LineData[];
  ema?: LineData[];
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

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart
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

    // Add Candlestick Series
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderVisible: false,
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
    });
    candleSeriesRef.current = candleSeries as any;

    // Add SMA Series
    const smaSeries = chart.addSeries(LineSeries, {
      color: "#2962FF",
      lineWidth: 2,
    });
    smaSeriesRef.current = smaSeries as any;

    // Add EMA Series
    const emaSeries = chart.addSeries(LineSeries, {
      color: "#FF6D00",
      lineWidth: 2,
    });
    emaSeriesRef.current = emaSeries as any;

    // Add Volume Series
    const volumeSeries = chart.addSeries(HistogramSeries, {
      color: "#26a69a",
      priceFormat: {
        type: "volume",
      },
      priceScaleId: "", // overlay
    });
    volumeSeriesRef.current = volumeSeries as any;
    
    // Scale Volume to bottom 20%
    chart.priceScale("").applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    // Handle Resize
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
    // Update data when it changes
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
    }

    if (smaSeriesRef.current && sma.length > 0) {
      smaSeriesRef.current.setData(sma as any);
    }
    
    if (emaSeriesRef.current && ema.length > 0) {
      emaSeriesRef.current.setData(ema as any);
    }

  }, [data, sma, ema]);

  return <div ref={chartContainerRef} style={{ width: "100%", position: "relative" }} />;
};

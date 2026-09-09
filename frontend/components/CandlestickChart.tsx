"use client";

import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, IChartApi, ISeriesApi, CandlestickSeries, HistogramSeries } from 'lightweight-charts';

interface OHLCV {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export default function CandlestickChart({ data }: { data: OHLCV[] }) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const handleResize = () => {
      if (chartRef.current && chartContainerRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#f8fafc' }, // slate-50
        textColor: '#334155', // navy-700
      },
      grid: {
        vertLines: { color: '#e2e8f0' },
        horzLines: { color: '#e2e8f0' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
      timeScale: {
        timeVisible: false,
        secondsVisible: false,
      },
      crosshair: {
        mode: 1, // Magnet
      }
    });

    chartRef.current = chart;

    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#16a34a', // success-600
      downColor: '#dc2626', // danger-600
      borderVisible: false,
      wickUpColor: '#16a34a',
      wickDownColor: '#dc2626',
    });

    const volumeSeries = chart.addSeries(HistogramSeries, {
      color: '#cbd5e1',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '', // set as an overlay
    });
    
    chart.priceScale('').applyOptions({
      scaleMargins: {
        top: 0.8, // highest point of the series will be at 80% of the chart height
        bottom: 0,
      },
    });

    // Process data
    const uniqueData = Array.from(new Map(data.map(d => [new Date(d.timestamp).getTime(), d])).values());
    const formattedData = uniqueData.map(d => ({
      time: new Date(d.timestamp).getTime() / 1000,
      open: Number(d.open),
      high: Number(d.high),
      low: Number(d.low),
      close: Number(d.close),
    })).sort((a, b) => (a.time as number) - (b.time as number));

    const volumeData = uniqueData.map(d => ({
      time: new Date(d.timestamp).getTime() / 1000,
      value: Number(d.volume),
      color: Number(d.close) > Number(d.open) ? 'rgba(22, 163, 74, 0.3)' : 'rgba(220, 38, 38, 0.3)'
    })).sort((a, b) => (a.time as number) - (b.time as number));

    candlestickSeries.setData(formattedData as any);
    volumeSeries.setData(volumeData as any);

    chart.timeScale().fitContent();

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data]);

  return <div ref={chartContainerRef} className="w-full h-full" />;
}

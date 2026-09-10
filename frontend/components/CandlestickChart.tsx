"use client";

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { createChart, ColorType, IChartApi, ISeriesApi, CandlestickSeries, HistogramSeries, Time } from 'lightweight-charts';
import { MousePointer2, Minus, Square, Type, Undo, Redo, Trash2, AlignJustify, MoveDiagonal } from 'lucide-react';

interface OHLCV {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

type Point = { time: number; price: number };
type DrawingType = 'cursor' | 'trendline' | 'horizontalLine' | 'rectangle' | 'fibonacci' | 'text';

interface Drawing {
  id: string;
  type: DrawingType;
  points: Point[];
  text?: string;
  color?: string;
}

export default function CandlestickChart({ data, symbol, userId = 'local_user' }: { data: OHLCV[], symbol?: string, userId?: string }) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  // Drawing state
  const [activeTool, setActiveTool] = useState<DrawingType>('cursor');
  const [drawings, setDrawings] = useState<Drawing[]>([]);
  const [currentDrawing, setCurrentDrawing] = useState<Drawing | null>(null);
  const [history, setHistory] = useState<Drawing[][]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [selectedDrawingId, setSelectedDrawingId] = useState<string | null>(null);
  
  // Render state for SVG
  const [renderedDrawings, setRenderedDrawings] = useState<any[]>([]);

  // Load from local storage
  useEffect(() => {
    if (symbol && userId) {
      const stored = localStorage.getItem(`borsa-takip:drawings:v1:${userId}:${symbol}`);
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          setDrawings(parsed);
          setHistory([parsed]);
          setHistoryIndex(0);
        } catch(e) {}
      }
    }
  }, [symbol, userId]);

  // Save to local storage
  useEffect(() => {
    if (symbol && userId && historyIndex >= 0) {
      localStorage.setItem(`borsa-takip:drawings:v1:${userId}:${symbol}`, JSON.stringify(drawings));
    }
  }, [drawings, symbol, userId, historyIndex]);

  const saveState = (newDrawings: Drawing[]) => {
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push(newDrawings);
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
    setDrawings(newDrawings);
  };

  const undo = () => {
    if (historyIndex > 0) {
      setHistoryIndex(historyIndex - 1);
      setDrawings(history[historyIndex - 1]);
    }
  };

  const redo = () => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex(historyIndex + 1);
      setDrawings(history[historyIndex + 1]);
    }
  };

  const clearAll = () => {
    saveState([]);
    setSelectedDrawingId(null);
  };

  const deleteSelected = () => {
    if (selectedDrawingId) {
      saveState(drawings.filter(d => d.id !== selectedDrawingId));
      setSelectedDrawingId(null);
    }
  };

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const handleResize = () => {
      if (chartRef.current && chartContainerRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
        updateRenderedDrawings();
      }
    };

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#f8fafc' },
        textColor: '#334155',
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
        mode: 1,
      }
    });

    chartRef.current = chart;

    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#16a34a',
      downColor: '#dc2626',
      borderVisible: false,
      wickUpColor: '#16a34a',
      wickDownColor: '#dc2626',
    });
    seriesRef.current = candlestickSeries;

    const volumeSeries = chart.addSeries(HistogramSeries, {
      color: '#cbd5e1',
      priceFormat: { type: 'volume' },
      priceScaleId: '',
    });
    
    chart.priceScale('').applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

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

    const onViewportChange = () => {
      updateRenderedDrawings();
    };

    chart.timeScale().subscribeVisibleTimeRangeChange(onViewportChange);
    chart.timeScale().subscribeVisibleLogicalRangeChange(onViewportChange);

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.timeScale().unsubscribeVisibleTimeRangeChange(onViewportChange);
      chart.timeScale().unsubscribeVisibleLogicalRangeChange(onViewportChange);
      chart.remove();
    };
  }, [data]);

  // Update chart options based on active tool
  useEffect(() => {
    if (chartRef.current) {
      const isCursor = activeTool === 'cursor';
      chartRef.current.applyOptions({
        handleScroll: isCursor,
        handleScale: isCursor,
        crosshair: {
          mode: isCursor ? 1 : 0, // crosshair style
        }
      });
    }
  }, [activeTool]);

  const getLogicalPoint = (clientX: number, clientY: number): Point | null => {
    if (!chartRef.current || !seriesRef.current || !chartContainerRef.current) return null;
    const rect = chartContainerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const y = clientY - rect.top;
    
    const time = chartRef.current.timeScale().coordinateToTime(x);
    const price = seriesRef.current.coordinateToPrice(y);
    
    if (time === null || price === null) return null;
    return { time: time as number, price };
  };

  const getPixelPoint = (point: Point) => {
    if (!chartRef.current || !seriesRef.current) return null;
    const x = chartRef.current.timeScale().timeToCoordinate(point.time as Time);
    const y = seriesRef.current.priceToCoordinate(point.price);
    if (x === null || y === null) return null;
    return { x, y };
  };

  const drawingsRef = useRef(drawings);
  const currentDrawingRef = useRef(currentDrawing);

  useEffect(() => {
    drawingsRef.current = drawings;
  }, [drawings]);

  useEffect(() => {
    currentDrawingRef.current = currentDrawing;
  }, [currentDrawing]);

  const updateRenderedDrawings = useCallback(() => {
    if (!chartRef.current || !seriesRef.current) return;
    
    const d = drawingsRef.current;
    const cd = currentDrawingRef.current;
    const allDrawings = cd ? [...d, cd] : d;
    
    const rendered = allDrawings.map(d => {
      // B7. Don't delete if outside viewport, just skip rendering points that can't be mapped
      const pxPoints = d.points.map(p => getPixelPoint(p)).filter(p => p !== null) as {x:number, y:number}[];
      return { ...d, pxPoints };
    });
    
    setRenderedDrawings(rendered);
  }, []);

  useEffect(() => {
    updateRenderedDrawings();
  }, [drawings, currentDrawing, updateRenderedDrawings]);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (activeTool === 'cursor') {
      // Find if clicked on a drawing to select it
      // Simple implementation: just deselect for now unless we implement complex hit testing
      setSelectedDrawingId(null);
      return;
    }

    const point = getLogicalPoint(e.clientX, e.clientY);
    if (!point) return;

    if (activeTool === 'text') {
      const text = window.prompt("Metin giriniz:");
      if (text) {
        const newDrawing: Drawing = {
          id: Date.now().toString(),
          type: 'text',
          points: [point],
          text,
          color: '#0f172a'
        };
        saveState([...drawings, newDrawing]);
      }
      setActiveTool('cursor');
      return;
    }

    if (activeTool === 'horizontalLine') {
      const newDrawing: Drawing = {
        id: Date.now().toString(),
        type: 'horizontalLine',
        points: [point],
        color: '#3b82f6'
      };
      saveState([...drawings, newDrawing]);
      setActiveTool('cursor');
      return;
    }

    // Two-point drawings
    setCurrentDrawing({
      id: Date.now().toString(),
      type: activeTool as DrawingType,
      points: [point, point],
      color: '#3b82f6'
    });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!currentDrawing) return;
    const point = getLogicalPoint(e.clientX, e.clientY);
    if (!point) return;

    setCurrentDrawing({
      ...currentDrawing,
      points: [currentDrawing.points[0], point]
    });
  };

  const handleMouseUp = () => {
    if (currentDrawing) {
      saveState([...drawings, currentDrawing]);
      setCurrentDrawing(null);
      setActiveTool('cursor');
    }
  };

  return (
    <div className="flex flex-col relative w-full h-full bg-slate-50">
      {/* Toolbar */}
      <div className="absolute top-2 left-2 z-10 flex flex-wrap gap-1 bg-white p-1 rounded-lg border border-slate-200 shadow-sm">
        <button onClick={() => setActiveTool('cursor')} className={`p-1.5 rounded hover:bg-slate-100 ${activeTool === 'cursor' ? 'bg-slate-100 text-primary-600' : 'text-slate-600'}`} title="İmleç">
          <MousePointer2 size={16} />
        </button>
        <button onClick={() => setActiveTool('trendline')} className={`p-1.5 rounded hover:bg-slate-100 ${activeTool === 'trendline' ? 'bg-slate-100 text-primary-600' : 'text-slate-600'}`} title="Trend Çizgisi">
          <MoveDiagonal size={16} />
        </button>
        <button onClick={() => setActiveTool('horizontalLine')} className={`p-1.5 rounded hover:bg-slate-100 ${activeTool === 'horizontalLine' ? 'bg-slate-100 text-primary-600' : 'text-slate-600'}`} title="Yatay Çizgi">
          <Minus size={16} />
        </button>
        <button onClick={() => setActiveTool('rectangle')} className={`p-1.5 rounded hover:bg-slate-100 ${activeTool === 'rectangle' ? 'bg-slate-100 text-primary-600' : 'text-slate-600'}`} title="Dikdörtgen">
          <Square size={16} />
        </button>
        <button onClick={() => setActiveTool('fibonacci')} className={`p-1.5 rounded hover:bg-slate-100 ${activeTool === 'fibonacci' ? 'bg-slate-100 text-primary-600' : 'text-slate-600'}`} title="Fibonacci Düzeltmesi">
          <AlignJustify size={16} />
        </button>
        <button onClick={() => setActiveTool('text')} className={`p-1.5 rounded hover:bg-slate-100 ${activeTool === 'text' ? 'bg-slate-100 text-primary-600' : 'text-slate-600'}`} title="Metin">
          <Type size={16} />
        </button>
        
        <div className="w-px bg-slate-200 mx-1"></div>
        
        <button onClick={undo} disabled={historyIndex <= 0} className="p-1.5 rounded hover:bg-slate-100 text-slate-600 disabled:opacity-30" title="Geri Al">
          <Undo size={16} />
        </button>
        <button onClick={redo} disabled={historyIndex >= history.length - 1} className="p-1.5 rounded hover:bg-slate-100 text-slate-600 disabled:opacity-30" title="İleri Al">
          <Redo size={16} />
        </button>
        <button onClick={clearAll} className="p-1.5 rounded hover:bg-red-50 text-red-500" title="Tümünü Temizle">
          <Trash2 size={16} />
        </button>
      </div>

      <div 
        ref={chartContainerRef} 
        className="flex-1 w-full relative outline-none"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {/* SVG Overlay for Drawings */}
        <svg 
          className="absolute inset-0 w-full h-full pointer-events-none z-[5]" 
          style={{ overflow: 'hidden' }}
        >
          {renderedDrawings.map(d => {
            if (d.pxPoints.length === 0) return null;
            const isSelected = d.id === selectedDrawingId;
            const strokeColor = isSelected ? '#f59e0b' : (d.color || '#3b82f6');
            const strokeWidth = isSelected ? 3 : 2;

            if (d.type === 'trendline' && d.pxPoints.length === 2) {
              return <line key={d.id} x1={d.pxPoints[0].x} y1={d.pxPoints[0].y} x2={d.pxPoints[1].x} y2={d.pxPoints[1].y} stroke={strokeColor} strokeWidth={strokeWidth} />;
            }
            if (d.type === 'horizontalLine' && d.pxPoints.length >= 1) {
              return <line key={d.id} x1={0} y1={d.pxPoints[0].y} x2="100%" y2={d.pxPoints[0].y} stroke={strokeColor} strokeWidth={strokeWidth} strokeDasharray="4 4" />;
            }
            if (d.type === 'rectangle' && d.pxPoints.length === 2) {
              const x = Math.min(d.pxPoints[0].x, d.pxPoints[1].x);
              const y = Math.min(d.pxPoints[0].y, d.pxPoints[1].y);
              const w = Math.abs(d.pxPoints[0].x - d.pxPoints[1].x);
              const h = Math.abs(d.pxPoints[0].y - d.pxPoints[1].y);
              return <rect key={d.id} x={x} y={y} width={w} height={h} stroke={strokeColor} strokeWidth={strokeWidth} fill={`${strokeColor}20`} />;
            }
            if (d.type === 'fibonacci' && d.pxPoints.length === 2) {
              const y1 = d.pxPoints[0].y;
              const y2 = d.pxPoints[1].y;
              const diff = y2 - y1;
              const levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1];
              return (
                <g key={d.id}>
                  <line x1={d.pxPoints[0].x} y1={y1} x2={d.pxPoints[1].x} y2={y2} stroke={strokeColor} strokeWidth={1} strokeDasharray="2 2" />
                  {levels.map(l => {
                    const y = y1 + diff * l;
                    return (
                      <g key={`${d.id}-${l}`}>
                        <line x1={0} y1={y} x2="100%" y2={y} stroke={strokeColor} strokeWidth={1} opacity={0.6} />
                        <text x={10} y={y - 4} fill={strokeColor} fontSize={10} fontWeight="bold">{(l * 100).toFixed(1)}%</text>
                      </g>
                    );
                  })}
                </g>
              );
            }
            if (d.type === 'text' && d.pxPoints.length >= 1) {
              return <text key={d.id} x={d.pxPoints[0].x} y={d.pxPoints[0].y} fill={strokeColor} fontSize={14} fontWeight="bold" style={{ userSelect: 'none' }}>{d.text}</text>;
            }
            return null;
          })}
        </svg>
      </div>
    </div>
  );
}

import { describe, it, expect } from 'vitest';
import { formatTry, formatPercent, formatQuantity, colorForSymbol, CASH_COLOR, getProfitLossColorClass, DATA_STATE_CONFIG } from '../lib/financialUi';

describe('Financial Formatters and Colors (Phase 23)', () => {
  it('formats TRY correctly', () => {
    expect(formatTry(10000)).toBe("10.000,00 ₺");
    expect(formatTry(299.25)).toBe("299,25 ₺");
    expect(formatTry(0)).toBe("0,00 ₺");
    expect(formatTry(-39.42)).toBe("-39,42 ₺");
    expect(formatTry(null)).toBe("-");
    expect(formatTry(undefined)).toBe("-");
  });

  it('formats percentages correctly', () => {
    expect(formatPercent(12.34)).toBe("12,34%");
    expect(formatPercent(5)).toBe("5,0%");
    expect(formatPercent(0)).toBe("0,0%");
    expect(formatPercent(-1.5)).toBe("-1,5%");
  });

  it('formats quantities correctly', () => {
    expect(formatQuantity(100)).toBe("100");
    expect(formatQuantity(1000.5)).toBe("1.000,5");
    expect(formatQuantity(0)).toBe("0");
  });

  it('assigns deterministic categorical colors to symbols', () => {
    const colorA = colorForSymbol('THYAO');
    const colorB = colorForSymbol('AEFES');
    
    // Should be deterministic
    expect(colorForSymbol('THYAO')).toBe(colorA);
    expect(colorForSymbol('AEFES')).toBe(colorB);
    
    // Cash color should be dedicated
    expect(colorForSymbol('Nakit')).toBe(CASH_COLOR);
    expect(colorA).not.toBe(colorB);
    expect(colorA).not.toBe(CASH_COLOR);
  });

  it('applies correct P/L color classes', () => {
    expect(getProfitLossColorClass(150)).toBe("text-emerald-600");
    expect(getProfitLossColorClass(-50)).toBe("text-rose-600");
    expect(getProfitLossColorClass(0)).toBe("text-slate-600");
    expect(getProfitLossColorClass("100")).toBe("text-emerald-600");
  });

  it('defines correct data state badges', () => {
    expect(DATA_STATE_CONFIG["LIVE"].label).toBe("CANLI");
    expect(DATA_STATE_CONFIG["DELAYED"].label).toBe("GECİKMELİ");
    expect(DATA_STATE_CONFIG["EOD"].label).toBe("GÜN SONU");
    expect(DATA_STATE_CONFIG["STALE"].label).toBe("GÜNCEL DEĞİL");
    expect(DATA_STATE_CONFIG["MOCK"].label).toBe("TEST VERİSİ");
    expect(DATA_STATE_CONFIG["UNAVAILABLE"].label).toBe("VERİ YOK");
  });
});

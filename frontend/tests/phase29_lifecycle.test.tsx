import { describe, it, expect } from 'vitest';
import { formatHealthState, formatAction, translateReasonCode } from '../components/PositionLifecycleRow';
import { LifecycleHealthState, LifecycleAction } from '../types/lifecycle';

describe('Phase 29 Lifecycle Formatting Helpers', () => {
  it('formats STABLE correctly', () => {
    expect(formatHealthState(LifecycleHealthState.STABLE).label).toBe('Stabil');
  });

  it('formats WATCH correctly', () => {
    expect(formatHealthState(LifecycleHealthState.WATCH).label).toBe('İzle');
  });

  it('formats CONFIRMED_DETERIORATION correctly', () => {
    expect(formatHealthState(LifecycleHealthState.CONFIRMED_DETERIORATION).label).toBe('Bozulma doğrulandı');
  });

  it('formats RECOVERING correctly', () => {
    expect(formatHealthState(LifecycleHealthState.RECOVERING).label).toBe('Toparlanıyor');
  });

  it('formats HOLD correctly', () => {
    expect(formatAction(LifecycleAction.HOLD).label).toBe('Bekle');
  });

  it('formats CONSIDER_ADD correctly', () => {
    expect(formatAction(LifecycleAction.CONSIDER_ADD).label).toBe('Artırmayı değerlendir');
  });

  it('formats CONSIDER_REDUCE correctly', () => {
    expect(formatAction(LifecycleAction.CONSIDER_REDUCE).label).toBe('Azaltmayı değerlendir');
  });

  it('formats CONSIDER_EXIT correctly', () => {
    expect(formatAction(LifecycleAction.CONSIDER_EXIT).label).toBe('Çıkışı değerlendir');
  });

  it('formats NO_ACTION_DATA / insufficient data correctly', () => {
    expect(formatAction(LifecycleAction.NO_ACTION_DATA).label).toBe('Veri yetersiz');
  });

  it('translates reason codes correctly', () => {
    expect(translateReasonCode('PARTIAL_REDUCTION_NOT_EXECUTABLE')).toBe('Pozisyon 1 adet olduğu için kısmi azaltma uygulanabilir değil.');
    expect(translateReasonCode('EXIT_DETERIORATION')).toBe('Çıkış şartları sağlandı.');
    expect(translateReasonCode('UNKNOWN_CODE')).toBe('Ek değerlendirme nedeni mevcut.');
  });
});

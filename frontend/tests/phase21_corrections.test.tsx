import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

// Mock dependencies
vi.mock('@tanstack/react-query', () => ({
  useQuery: vi.fn().mockImplementation(({ queryKey }) => {
    if (queryKey[2] === 'basic') return { data: { name: 'Türk Hava Yolları A.O.' }, isLoading: false };
    if (queryKey[2] === 'context') return { 
      data: { availability: { kap: false, news: false }, disclosures: [], news: [] }, 
      isLoading: false 
    };
    if (queryKey[2] === 'technical') return { 
      data: { indicators: [{ name: 'RSI_14', value: 45 }] }, // NO MACD
      isLoading: false 
    };
    return { data: null, isLoading: false };
  }),
}));
vi.mock('next/navigation', () => ({
  useParams: () => ({ symbol: 'THYAO' }),
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), prefetch: vi.fn() }),
}));
vi.mock('@/components/NetworkProvider', () => ({
  useNetwork: () => ({ isOnline: true }),
}));

import InstrumentDetail from '../app/(protected)/instruments/[symbol]/page';
import Login from '../app/(auth)/login/page';

describe('Phase 21 Corrections', () => {
  it('does not contain dead password reset link in Login', () => {
    render(<Login />);
    const link = screen.queryByText('Şifremi Unuttum');
    expect(link).toBeNull();
  });

  it('does not claim Gerçek zamanlı', () => {
    render(<Login />);
    const text = screen.queryByText(/Gerçek zamanlı/i);
    expect(text).toBeNull();
  });

  it('renders company name properly', () => {
    render(<InstrumentDetail />);
    expect(screen.getByText('Türk Hava Yolları A.O.')).toBeDefined();
  });

  it('displays Yetersiz Veri for missing MACD', () => {
    render(<InstrumentDetail />);
    const elements = screen.getAllByText('MACD Trend');
    expect(elements[0].nextElementSibling?.textContent).toBe('Yetersiz Veri');
  });

});

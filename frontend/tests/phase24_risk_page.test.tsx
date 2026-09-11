import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import PortfolioRiskPage from '../app/(protected)/portfolios/[id]/risk/page';
import { useQuery } from '@tanstack/react-query';
import React from 'react';

// Mock dependencies
vi.mock('@tanstack/react-query', () => ({
  useQuery: vi.fn(),
}));

vi.mock('next/navigation', () => ({
  useParams: () => ({ id: '1' }),
}));

// Mock Lucide icons
vi.mock('lucide-react', () => ({
  AlertCircle: () => <div data-testid="icon-alert" />,
  ShieldAlert: () => <div data-testid="icon-shield" />,
  PieChart: () => <div data-testid="icon-pie" />,
}));

describe('PortfolioRiskPage (Phase 24)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly with realistic numeric mock data, avoiding scientific notation', () => {
    (useQuery as any).mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        portfolio_id: 1,
        total_market_value: 10000.5,
        invested_exposure: 6353.4200000000000000,
        cash_exposure: 3647.08,
        cash_weight_percentage: 36.468,
        invested_weight_percentage: 63.5319,
        historical_var_95_1d: 500.123,
        positions_exposure: [
          {
            instrument_id: 1,
            symbol: 'THYAO',
            weight_percentage: 63.5319,
            market_value: 6353.42,
            is_stale: false,
          }
        ],
        limit_violations: [],
        data_freshness: 'LIVE',
        coverage_percentage: 100
      }
    });

    render(<PortfolioRiskPage />);
    
    // Check formatted cash weight
    expect(screen.getByText('36,47%')).toBeDefined();
    
    // Check formatted invested weight
    expect(screen.getByText('63,53%')).toBeDefined();
    
    // Check historical var
    expect(screen.getByText('500,12 ₺')).toBeDefined();

    // Check progress bar symbol
    expect(screen.getByText('THYAO')).toBeDefined();

    // Check DataStateBadge mapped to CANLI
    expect(screen.getByText('CANLI')).toBeDefined();
    
    // Should NOT contain raw 6353.4200000000000000
    const rawVal = screen.queryByText(/6353\.4200000000000000/);
    expect(rawVal).toBeNull();
  });

  it('handles scientific notation 0E+14 safely via formatter', () => {
    (useQuery as any).mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        portfolio_id: 1,
        total_market_value: 10000,
        invested_exposure: 0,
        cash_exposure: 10000,
        cash_weight_percentage: 100,
        invested_weight_percentage: "0E+14", // simulated backend dump
        historical_var_95_1d: null,
        positions_exposure: [],
        limit_violations: [],
        data_freshness: 'LIVE',
        coverage_percentage: 100
      }
    });

    render(<PortfolioRiskPage />);
    
    // Since invested_weight_percentage="0E+14", formatPercent("0E+14") -> Number(0) -> 0,00%
    expect(screen.getByText('0,0%')).toBeDefined();
    
    const scientificNode = screen.queryByText(/0E\+14/);
    expect(scientificNode).toBeNull();
  });
});

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import DashboardPage from '../app/(protected)/dashboard/page';
import { useQuery } from '@tanstack/react-query';
import { useNetwork } from '@/components/NetworkProvider';
import React from 'react';

// Mock dependencies
vi.mock('@tanstack/react-query', () => ({
  useQuery: vi.fn(),
}));

vi.mock('@/components/NetworkProvider', () => ({
  useNetwork: vi.fn(),
}));

// Mock Lucide icons
vi.mock('lucide-react', () => ({
  Activity: () => <div data-testid="icon-activity" />,
  WifiOff: () => <div data-testid="icon-wifioff" />,
  Briefcase: () => <div data-testid="icon-briefcase" />,
  TrendingUp: () => <div data-testid="icon-trendingup" />,
  TrendingDown: () => <div data-testid="icon-trendingdown" />,
  Clock: () => <div data-testid="icon-clock" />,
  AlertCircle: () => <div data-testid="icon-alert" />,
  ArrowRight: () => <div data-testid="icon-arrowright" />,
}));

describe('DashboardPage (Phase 25)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (useNetwork as any).mockReturnValue({ isOnline: true });
  });

  it('renders portfolio cards with correctly formatted values and no zero dump', () => {
    (useQuery as any).mockReturnValue({
      isLoading: false,
      isError: false,
      data: [
        {
          id: 1,
          name: 'Ana Portföy',
          portfolio_type: 'REAL',
          total_market_value: 125000.5,
        },
        {
          id: 2,
          name: 'Yedek Portföy',
          portfolio_type: 'SIMULATED',
          total_market_value: null, // No positions/cash yet
        }
      ]
    });

    render(<DashboardPage />);
    
    expect(screen.getByText('Ana Portföy')).toBeDefined();
    // 125000.5 should format to "125.000,50 ₺" via formatTry
    expect(screen.getByText('125.000,50 ₺')).toBeDefined();
    
    expect(screen.getByText('Yedek Portföy')).toBeDefined();
    // Null should safely fallback to 0,00 ₺
    expect(screen.getByText('0,00 ₺')).toBeDefined();
    
    // Make sure we didn't render the word NaN or undefined
    const nanVal = screen.queryByText(/NaN/i);
    expect(nanVal).toBeNull();
  });
});

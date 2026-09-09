import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import DecisionCard from '../components/DecisionCard';

describe('DecisionCard', () => {
  it('renders YETERSIZ VERI correctly', () => {
    const mockDecision = {
      decision_state: 'INSUFFICIENT_DATA',
      market_view: 'HOLD',
      personal_action: null,
      data_quality_score: 40,
      overall_market_score: 40,
      technical_score: 0,
      fundamental_score: 0,
      missing_data: true,
      engine_version: 'v2.0'
    };

    render(<DecisionCard decision={mockDecision as any} symbol="AEFES" />);
    
    expect(screen.getByText(/YETERS/)).toBeDefined();
  });
});

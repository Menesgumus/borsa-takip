import { render } from '@testing-library/react';
import CandlestickChart from '../components/CandlestickChart';
import fs from 'fs';
import path from 'path';
import { describe, it, expect } from 'vitest';

describe('CandlestickChart', () => {
  it('does not contain hardcoded test@test.com for localStorage persistence', () => {
    const fileContent = fs.readFileSync(path.join(__dirname, '../components/CandlestickChart.tsx'), 'utf-8');
    
    // The specific hardcoded literal should not be present
    expect(fileContent).not.toContain('drawings_test@test.com_');
    
    // Instead it should use the new pattern
    expect(fileContent).toContain('borsa-takip:drawings:v1:${userId}:${symbol}');
  });
});

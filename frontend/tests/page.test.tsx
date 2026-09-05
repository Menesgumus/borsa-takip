import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Page from '../app/page';

describe('Page', () => {
  it('renders a heading', () => {
    render(React.createElement(Page));
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading).toBeDefined();
    expect(heading.textContent).toBe('Borsa Takip');
  });
});

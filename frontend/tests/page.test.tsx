import { describe, it, expect, vi } from 'vitest';
import Page from '../app/page';

vi.mock('next/navigation', () => ({
  redirect: vi.fn(),
}));

import { redirect } from 'next/navigation';

describe('Page', () => {
  it('redirects to dashboard', () => {
    Page();
    expect(redirect).toHaveBeenCalledWith('/dashboard');
  });
});

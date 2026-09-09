import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import AuthLayout from '../app/(auth)/layout';
import ProtectedLayout from '../app/(protected)/layout';
import * as auth from '../lib/auth';
import * as navigation from 'next/navigation';

vi.mock('../lib/auth', () => ({
  getSession: vi.fn(),
}));

vi.mock('next/navigation', () => ({
  redirect: vi.fn(() => { throw new Error('NEXT_REDIRECT'); }),
}));

// Mock AppShell so it doesn't try to render complex client logic in test
vi.mock('../components/AppShell', () => ({
  default: ({ children }: any) => <div>{children}</div>,
}));

describe('Layout Auth Logic', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('B) valid session + /dashboard -> dashboard (ProtectedLayout allows)', async () => {
    vi.mocked(auth.getSession).mockResolvedValueOnce({ email: 'test@test.com' });
    try { await ProtectedLayout({ children: 'content' }); } catch (e) {}
    expect(navigation.redirect).not.toHaveBeenCalled();
  });

  it('C) stale/invalid cookie + /dashboard -> /login, NO loop (ProtectedLayout redirects)', async () => {
    vi.mocked(auth.getSession).mockResolvedValueOnce(null);
    try { await ProtectedLayout({ children: 'content' }); } catch (e) {}
    expect(navigation.redirect).toHaveBeenCalledWith('/login');
  });

  it('D) stale/invalid cookie + /login -> login remains accessible (AuthLayout allows)', async () => {
    vi.mocked(auth.getSession).mockResolvedValueOnce(null);
    try { await AuthLayout({ children: 'content' }); } catch (e) {}
    expect(navigation.redirect).not.toHaveBeenCalled();
  });

  it('E) valid session + /login -> AuthLayout redirects to /dashboard', async () => {
    vi.mocked(auth.getSession).mockResolvedValueOnce({ email: 'test@test.com' });
    try { await AuthLayout({ children: 'content' }); } catch (e) {}
    expect(navigation.redirect).toHaveBeenCalledWith('/dashboard');
  });
});

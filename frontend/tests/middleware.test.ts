import { describe, it, expect, vi } from 'vitest';
import { middleware } from '../middleware';
import { NextRequest } from 'next/server';

vi.mock('next/server', () => {
  return {
    NextResponse: {
      redirect: vi.fn((url) => ({ status: 307, url: url.toString() })),
      next: vi.fn(() => ({ status: 200, type: 'next' })),
    },
  };
});

describe('Middleware Auth Logic', () => {
  it('A) no cookie + /dashboard -> /login', () => {
    const req = {
      nextUrl: { pathname: '/dashboard' },
      url: 'http://localhost/dashboard',
      cookies: { has: () => false },
    } as unknown as NextRequest;

    const res = middleware(req) as any;
    expect(res.status).toBe(307);
    expect(res.url).toContain('/login');
  });

  it('B) valid session + /dashboard -> dashboard (allows next)', () => {
    const req = {
      nextUrl: { pathname: '/dashboard' },
      url: 'http://localhost/dashboard',
      cookies: { has: () => true },
    } as unknown as NextRequest;

    const res = middleware(req) as any;
    expect(res.status).toBe(200);
    expect(res.type).toBe('next');
  });

  it('C,D) stale/invalid cookie + /login -> login remains accessible (allows next)', () => {
    const req = {
      nextUrl: { pathname: '/login' },
      url: 'http://localhost/login',
      cookies: { has: () => true }, // Middleware just sees cookie, lets it pass to layout!
    } as unknown as NextRequest;

    const res = middleware(req) as any;
    expect(res.status).toBe(200);
    expect(res.type).toBe('next');
  });

  it('E) valid session + /login -> login remains accessible in middleware, auth layout will handle the redirect', () => {
    // Middleware allows it
    const req = {
      nextUrl: { pathname: '/login' },
      url: 'http://localhost/login',
      cookies: { has: () => true },
    } as unknown as NextRequest;

    const res = middleware(req) as any;
    expect(res.status).toBe(200);
  });
});

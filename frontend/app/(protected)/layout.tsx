import React from 'react';
import { redirect } from 'next/navigation';
import { getSession, getProfile } from '@/lib/auth';
import { headers } from 'next/headers';
import AppShell from '@/components/AppShell';

export default async function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getSession();

  if (!session) {
    redirect('/login');
  }

  const profile = await getProfile();
  const headersList = await headers();
  const pathname = headersList.get('x-pathname') || '';

  if (profile && profile.onboarding_completed === false && pathname !== '/onboarding') {
    redirect('/onboarding');
  }

  if (profile && profile.onboarding_completed === true && pathname === '/onboarding') {
    redirect('/dashboard');
  }

  return (
    <AppShell userEmail={session.email}>
      {children}
    </AppShell>
  );
}

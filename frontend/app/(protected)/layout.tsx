import React from 'react';
import { redirect } from 'next/navigation';
import { getSession } from '@/lib/auth';
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

  return (
    <AppShell userEmail={session.email}>
      {children}
    </AppShell>
  );
}

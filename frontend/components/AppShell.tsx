'use client';

import React from 'react';
import Sidebar from '@/components/Sidebar';
import { fetchApi } from '@/lib/api';

export default function AppShell({ 
  children, 
  userEmail 
}: { 
  children: React.ReactNode; 
  userEmail: string;
}) {
  const handleLogout = async () => {
    try {
      await fetchApi('/api/v1/auth/logout', { method: 'POST' });
    } catch (e) {
      console.error('Logout error', e);
    } finally {
      window.location.href = '/login';
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col lg:flex-row">
      <Sidebar userEmail={userEmail} onLogout={handleLogout} />
      
      <div className="flex-1 flex flex-col lg:pl-64 min-w-0">
        <main className="flex-1 p-4 lg:p-8 overflow-x-hidden">
          <div className="mx-auto max-w-7xl">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

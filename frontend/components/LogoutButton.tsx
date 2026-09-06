'use client';

import { fetchApi } from '@/lib/api';
import { useState } from 'react';

export default function LogoutButton() {
  const [loading, setLoading] = useState(false);

  const handleLogout = async () => {
    setLoading(true);
    try {
      await fetchApi('/api/v1/auth/logout', { method: 'POST' });
    } catch (e) {
      console.error('Logout error', e);
    } finally {
      window.location.href = '/login';
    }
  };

  return (
    <button 
      onClick={handleLogout}
      disabled={loading}
      className="text-sm text-red-600 hover:underline disabled:opacity-50"
    >
      {loading ? 'Çıkış yapılıyor...' : 'Çıkış Yap'}
    </button>
  );
}

import React from 'react';

export default async function Home() {
  let apiStatus = 'Unknown';
  try {
    const apiUrl = process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://api:8000';
    const res = await fetch(`${apiUrl}/health/ready`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      apiStatus = data.status === 'ok' ? 'DB_REDIS_OK' : 'ERROR';
    }
  } catch (e) {
    apiStatus = 'FETCH_FAILED';
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1 className="text-4xl font-bold">Borsa Takip</h1>
      <p>Frontend hazır!</p>
      <div data-testid="api-status">API/DB Status: {apiStatus}</div>
    </main>
  );
}

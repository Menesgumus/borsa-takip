'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { fetchApi } from '@/lib/api';

export default function OnboardingPage() {
  const router = useRouter();
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [riskTolerance, setRiskTolerance] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleComplete = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!riskTolerance) {
      setError('Lütfen risk toleransınızı seçin.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await fetchApi('/api/v1/users/profile', {
        method: 'PUT',
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          risk_tolerance: riskTolerance,
          onboarding_completed: true,
        }),
      });
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } catch (err: any) {
      setError(err.message || 'Profil güncellenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-10 p-6 bg-white shadow-md rounded-lg">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Hoş Geldiniz</h2>
      <p className="text-gray-600 mb-8">Uygulamayı kullanmaya başlamadan önce lütfen profilinizi tamamlayın.</p>
      
      <form onSubmit={handleComplete} className="space-y-6">
        <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
          <div>
            <label htmlFor="firstName" className="block text-sm font-medium text-gray-700">
              Ad (İsteğe bağlı)
            </label>
            <div className="mt-1">
              <input
                type="text"
                name="firstName"
                id="firstName"
                className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
            </div>
          </div>

          <div>
            <label htmlFor="lastName" className="block text-sm font-medium text-gray-700">
              Soyad (İsteğe bağlı)
            </label>
            <div className="mt-1">
              <input
                type="text"
                name="lastName"
                id="lastName"
                className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div>
          <label htmlFor="riskTolerance" className="block text-sm font-medium text-gray-700">
            Risk Toleransı (Zorunlu)
          </label>
          <div className="mt-1">
            <select
              id="riskTolerance"
              name="riskTolerance"
              required
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md border"
              value={riskTolerance}
              onChange={(e) => setRiskTolerance(e.target.value)}
            >
              <option value="" disabled>Seçiniz</option>
              <option value="LOW">Düşük Risk</option>
              <option value="MEDIUM">Orta Risk</option>
              <option value="HIGH">Yüksek Risk</option>
            </select>
          </div>
          <p className="mt-2 text-sm text-gray-500">
            Yatırım stratejinizi belirlememize yardımcı olması için lütfen risk toleransınızı seçin.
          </p>
        </div>

        {error && (
          <div className="text-red-500 text-sm font-medium">
            {error}
          </div>
        )}

        <div className="pt-4 flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? 'Kaydediliyor...' : 'Tamamla ve Başla'}
          </button>
        </div>
      </form>
    </div>
  );
}

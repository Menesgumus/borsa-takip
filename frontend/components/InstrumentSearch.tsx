'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Search, Loader2 } from 'lucide-react';
import { fetchApi } from '@/lib/api';
import { useQuery } from '@tanstack/react-query';

export function InstrumentSearch() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);
  
  // Custom simple debounce inline to avoid missing hook dependencies
  const [debouncedSearch, setDebouncedSearch] = useState('');
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(searchTerm), 300);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  const { data, isLoading } = useQuery({
    queryKey: ['instruments', 'search', debouncedSearch],
    queryFn: async () => {
      if (!debouncedSearch || debouncedSearch.length < 2) return { items: [] };
      const res = await fetchApi(`/api/v1/instruments?search=${encodeURIComponent(debouncedSearch)}&size=10`);
      return res;
    },
    enabled: debouncedSearch.length >= 2,
    staleTime: 60000,
  });

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsFocused(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const results = (data as any)?.items || [];
  const showResults = isFocused && debouncedSearch.length >= 2;

  return (
    <div className="relative w-full max-w-lg" ref={wrapperRef}>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-slate-400" />
        </div>
        <input
          type="text"
          className="block w-full pl-10 pr-3 py-2 border border-navy-700 rounded-md leading-5 bg-navy-800 text-slate-200 placeholder-slate-400 focus:outline-none focus:bg-navy-900 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm transition-colors"
          placeholder="Sembol veya Varlık Ara (örn. THYAO, AAPL, GLDTR)"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onFocus={() => setIsFocused(true)}
        />
        {isLoading && debouncedSearch.length >= 2 && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <Loader2 className="h-4 w-4 text-slate-400 animate-spin" />
          </div>
        )}
      </div>

      {showResults && (
        <div className="absolute mt-1 w-full bg-navy-800 border border-navy-700 rounded-md shadow-lg z-50 max-h-60 overflow-auto">
          {results.length > 0 ? (
            <ul className="py-1">
              {results.map((inst: any) => (
                <li key={inst.symbol}>
                  <button
                    className="w-full text-left px-4 py-2 hover:bg-navy-700 focus:bg-navy-700 focus:outline-none transition-colors flex justify-between items-center"
                    onClick={() => {
                      setSearchTerm('');
                      setIsFocused(false);
                      router.push(`/instruments/${inst.symbol}`);
                    }}
                  >
                    <span className="font-medium text-white">{inst.symbol}</span>
                    <span className="text-sm text-slate-400 truncate ml-4">{inst.name}</span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="px-4 py-3 text-sm text-slate-400">
              {!isLoading && "Sonuç bulunamadı."}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

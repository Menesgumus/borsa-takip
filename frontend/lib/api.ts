const API_BASE_URL = '';

export class ApiError extends Error {
  constructor(public status: number, message: string, public code?: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  let baseUrl = '';
  if (typeof window === 'undefined') {
    baseUrl = process.env.INTERNAL_API_URL || 'http://127.0.0.1:8001';
  }
  const url = `${baseUrl}${endpoint}`;
  
  // Future: Add JWT token here
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');

  const config: RequestInit = {
    ...options,
    headers,
    credentials: 'include',
  };

  const response = await fetch(url, config);
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new ApiError(
      response.status,
      data?.error?.message || data?.detail || 'Bilinmeyen bir API hatası oluştu',
      data?.error?.code
    );
  }

  return data as T;
}

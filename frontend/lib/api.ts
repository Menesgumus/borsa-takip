const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export class ApiError extends Error {
  constructor(public status: number, message: string, public code?: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Future: Add JWT token here
  const headers = new Headers(options.headers);
  headers.set('Content-Type', 'application/json');

  const config: RequestInit = {
    ...options,
    headers,
  };

  const response = await fetch(url, config);
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new ApiError(
      response.status,
      data?.error?.message || 'Bilinmeyen bir API hatası oluştu',
      data?.error?.code
    );
  }

  return data as T;
}

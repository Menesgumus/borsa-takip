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
  
  const headers = new Headers(options.headers);
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  // Default timeout 8 seconds, can be overridden by passing signal in options
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 8000);

  const config: RequestInit = {
    ...options,
    headers,
    credentials: 'include',
    signal: options.signal || controller.signal,
  };

  try {
    const response = await fetch(url, config);
    clearTimeout(timeoutId);
    
    // Some endpoints might return 204 No Content
    if (response.status === 204) return null as T;

    const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new ApiError(
      response.status,
      data?.error?.message || data?.detail || 'Bilinmeyen bir API hatası oluştu',
      data?.error?.code
    );
  }

  return data as T;
  } catch (error: any) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error('İstek zaman aşımına uğradı');
    }
    throw error;
  }
}

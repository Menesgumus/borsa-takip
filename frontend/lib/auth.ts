import { cookies } from 'next/headers';
import { fetchApi } from './api';

export async function getSession() {
  const cookieStore = await cookies();
  const sessionToken = cookieStore.get('session_token')?.value;

  if (!sessionToken) {
    return null;
  }

  try {
    // We pass the cookie explicitly for the server-side fetch
    const user = await fetchApi<any>('/api/v1/auth/me', {
      headers: {
        Cookie: `session_token=${sessionToken}`,
      },
    });
    return user;
  } catch (error) {
    return null;
  }
}

export async function getProfile() {
  const cookieStore = await cookies();
  const sessionToken = cookieStore.get('session_token')?.value;

  if (!sessionToken) {
    return null;
  }

  try {
    const profile = await fetchApi<any>('/api/v1/users/profile', {
      headers: {
        Cookie: `session_token=${sessionToken}`,
      },
    });
    return profile;
  } catch (error) {
    return null;
  }
}

import api, { clearAuthTokens, setAuthTokens } from '@/shared/api/client';

export interface LoginPayload {
  username: string;
  password: string;
}

export interface AuthenticatedUser {
  id: number;
  username: string;
  email?: string | null;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  token_type: string;
  user?: AuthenticatedUser;
}

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>('/api/token', payload);
  setAuthTokens(data.access, data.refresh);
  return data;
}

export function logout(): void {
  clearAuthTokens();
}

export async function register(payload: LoginPayload): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>('/api/register', payload);
  setAuthTokens(data.access, data.refresh);
  return data;
}

export async function fetchCurrentUser(): Promise<AuthenticatedUser> {
  const { data } = await api.get<AuthenticatedUser>('/api/users/me');
  return data;
}

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY } from '@/shared/constants/storage';
import { getItem, removeItem, setItem } from '@/shared/utils/storage';

export interface RefreshTokenResponse {
  access: string;
  refresh?: string;
}

type RequestConfigWithRetry = AxiosRequestConfig & { _retry?: boolean };

const baseURL = import.meta.env.VITE_API_URL;

if (!baseURL) {
  console.warn('VITE_API_URL is not defined. API requests will fail until it is set.');
}

const api: AxiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const refreshClient: AxiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

let refreshPromise: Promise<string | null> | null = null;

function getAccessToken(): string | null {
  return getItem(ACCESS_TOKEN_KEY);
}

function getRefreshToken(): string | null {
  return getItem(REFRESH_TOKEN_KEY);
}

export function setAuthTokens(accessToken: string, refreshToken?: string): void {
  setItem(ACCESS_TOKEN_KEY, accessToken);
  if (refreshToken) {
    setItem(REFRESH_TOKEN_KEY, refreshToken);
  }
}

export function clearAuthTokens(): void {
  removeItem(ACCESS_TOKEN_KEY);
  removeItem(REFRESH_TOKEN_KEY);
}

async function requestAccessTokenRefresh(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    return null;
  }

  try {
    const response = await refreshClient.post<RefreshTokenResponse>('/api/token/refresh', {
      refresh_token: refreshToken,
    });

    const { access, refresh } = response.data;
    if (access) {
      setAuthTokens(access, refresh);
      return access;
    }
    return null;
  } catch (error) {
    clearAuthTokens();
    return null;
  }
}

async function getOrRefreshAccessToken(): Promise<string | null> {
  if (!refreshPromise) {
    refreshPromise = requestAccessTokenRefresh().finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const { response, config } = error;

    if (!response || !config) {
      return Promise.reject(error);
    }

    if (response.status === 401) {
      const requestConfig = config as RequestConfigWithRetry;

      if (requestConfig._retry) {
        clearAuthTokens();
        return Promise.reject(error);
      }

      requestConfig._retry = true;
      const newAccessToken = await getOrRefreshAccessToken();

      if (newAccessToken) {
        requestConfig.headers = {
          ...requestConfig.headers,
          Authorization: `Bearer ${newAccessToken}`,
        };
        return api(requestConfig);
      }
    }

    return Promise.reject(error);
  }
);

export function createCrudApi<TItem, TCreate = Partial<TItem>, TUpdate = Partial<TItem>>(resourcePath: string) {
  const normalizedPath = resourcePath.startsWith('/') ? resourcePath : `/${resourcePath}`;
  const collectionPath = normalizedPath.endsWith('/') ? normalizedPath : `${normalizedPath}/`;

  return {
    async list(params?: Record<string, unknown>): Promise<TItem[]> {
      const { data } = await api.get<TItem[]>(collectionPath, { params });
      return data;
    },
    async retrieve(id: string | number, params?: Record<string, unknown>): Promise<TItem> {
      const { data } = await api.get<TItem>(`${normalizedPath}/${id}`, { params });
      return data;
    },
    async create(payload: TCreate): Promise<TItem> {
      const { data } = await api.post<TItem>(collectionPath, payload);
      return data;
    },
    async update(id: string | number, payload: TUpdate): Promise<TItem> {
      const { data } = await api.put<TItem>(`${normalizedPath}/${id}`, payload);
      return data;
    },
    async partialUpdate(id: string | number, payload: Partial<TUpdate>): Promise<TItem> {
      const { data } = await api.patch<TItem>(`${normalizedPath}/${id}`, payload);
      return data;
    },
    async remove(id: string | number): Promise<void> {
      await api.delete(`${normalizedPath}/${id}`);
    },
  };
}

export default api;

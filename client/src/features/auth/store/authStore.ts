import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AxiosError } from 'axios';
import { AuthenticatedUser, login } from '@/features/auth/api';
import { clearAuthTokens, setAuthTokens } from '@/shared/api/client';
import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY, USER_KEY } from '@/shared/constants/storage';
import { getItem, removeItem, setItem } from '@/shared/utils/storage';

interface AuthState {
  user: AuthenticatedUser | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticating: boolean;
  isInitialized: boolean;
  error?: string | null;
  initialize: () => void;
  signIn: (username: string, password: string) => Promise<void>;
  signOut: () => void;
  setUser: (user: AuthenticatedUser | null) => void;
  setTokens: (access: string, refresh?: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticating: false,
      isInitialized: false,
      error: null,
      initialize: () => {
        const accessToken = getItem(ACCESS_TOKEN_KEY);
        const refreshToken = getItem(REFRESH_TOKEN_KEY);
        const userRaw = getItem(USER_KEY);

        set({
          accessToken,
          refreshToken,
          user: userRaw ? (JSON.parse(userRaw) as AuthenticatedUser) : null,
          error: null,
          isInitialized: true,
        });
      },
      signIn: async (username: string, password: string) => {
        set({ isAuthenticating: true, error: null });
        try {
          const response = await login({ username, password });
          setAuthTokens(response.access, response.refresh);
          setItem(USER_KEY, JSON.stringify(response.user ?? null));
          set({
            accessToken: response.access,
            refreshToken: response.refresh,
            user: response.user ?? null,
            isAuthenticating: false,
            isInitialized: true,
            error: null,
          });
        } catch (error) {
          let message = 'Unable to sign in. Please try again.';
          if (error instanceof AxiosError) {
            message =
              (error.response?.data as { detail?: string })?.detail ??
              error.message ??
              message;
          } else if (error instanceof Error) {
            message = error.message;
          }
          set({ isAuthenticating: false, error: message });
          throw error;
        }
      },
      signOut: () => {
        clearAuthTokens();
        removeItem(USER_KEY);
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          error: null,
          isInitialized: true,
        });
      },
      setUser: (user: AuthenticatedUser | null) => {
        setItem(USER_KEY, JSON.stringify(user));
        set({ user });
      },
      setTokens: (access: string, refresh?: string) => {
        setAuthTokens(access, refresh);
        set({
          accessToken: access,
          refreshToken: refresh ?? get().refreshToken,
        });
      },
    }),
    {
      name: 'mto360-auth',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
    }
  )
);

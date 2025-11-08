import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ThemeMode = 'light' | 'dark' | 'system';

export interface NotificationMessage {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  description?: string;
  createdAt: number;
}

interface UIState {
  theme: ThemeMode;
  isSidebarCollapsed: boolean;
  notifications: NotificationMessage[];
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (mode: ThemeMode) => void;
  pushNotification: (notification: Omit<NotificationMessage, 'createdAt'>) => void;
  dismissNotification: (id: string) => void;
  clearNotifications: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      theme: 'system',
      isSidebarCollapsed: false,
      notifications: [],
      toggleSidebar: () => {
        set((state) => ({ isSidebarCollapsed: !state.isSidebarCollapsed }));
      },
      setSidebarCollapsed: (collapsed: boolean) => set({ isSidebarCollapsed: collapsed }),
      setTheme: (mode: ThemeMode) => set({ theme: mode }),
      pushNotification: (notification) => {
        set((state) => ({
          notifications: [
            {
              ...notification,
              createdAt: Date.now(),
            },
            ...state.notifications,
          ].slice(0, 20),
        }));
      },
      dismissNotification: (id: string) => {
        set((state) => ({
          notifications: state.notifications.filter((item) => item.id !== id),
        }));
      },
      clearNotifications: () => set({ notifications: [] }),
    }),
    {
      name: 'mto360-ui',
      partialize: (state) => ({
        theme: state.theme,
        isSidebarCollapsed: state.isSidebarCollapsed,
      }),
    }
  )
);

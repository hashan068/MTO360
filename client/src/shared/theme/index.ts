import { theme } from 'antd';
import type { ThemeConfig } from 'antd/es/config-provider/context';

export type ThemePreference = 'light' | 'dark' | 'system';
export type ResolvedTheme = Exclude<ThemePreference, 'system'>;

const commonConfig: ThemeConfig = {
  token: {
    fontFamily:
      "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
    borderRadius: 8,
  },
  components: {
    Layout: {
      bodyBg: 'transparent',
    },
  },
};

const lightConfig: ThemeConfig = {
  algorithm: theme.defaultAlgorithm,
  token: {
    colorBgBase: '#ffffff',
    colorTextBase: '#1f2937',
  },
};

const darkConfig: ThemeConfig = {
  algorithm: theme.darkAlgorithm,
  token: {
    colorBgBase: '#0f172a',
    colorTextBase: '#f8fafc',
  },
};

export function getAntdThemeConfig(resolved: ResolvedTheme): ThemeConfig {
  const variantConfig = resolved === 'dark' ? darkConfig : lightConfig;
  return {
    ...commonConfig,
    ...variantConfig,
    token: {
      ...commonConfig.token,
      ...variantConfig.token,
    },
    components: {
      ...commonConfig.components,
      ...(variantConfig.components ?? {}),
    },
  };
}

export function syncThemeToDom(theme: ResolvedTheme): void {
  if (typeof document === 'undefined') {
    return;
  }

  document.documentElement.dataset.theme = theme;
}


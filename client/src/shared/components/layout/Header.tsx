import {
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  MoonOutlined,
  SunOutlined,
} from '@ant-design/icons';
import { Avatar, Button, Dropdown, Layout, Space, Switch, Typography } from 'antd';
import type { MenuProps } from 'antd';
import { useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/features/auth/store/authStore';
import { ThemeMode, useUIStore } from '@/shared/state/uiStore';
import NotificationBell from '@/components/NotificationBell';

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const signOut = useAuthStore((state) => state.signOut);
  const isCollapsed = useUIStore((state) => state.isSidebarCollapsed);
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);
  const theme = useUIStore((state) => state.theme);
  const setTheme = useUIStore((state) => state.setTheme);

  const pageTitle = useMemo(() => {
    const segments = location.pathname.split('/').filter(Boolean);
    if (segments.length === 0) return 'Dashboard';
    return segments.map((segment) => segment.replace(/-/g, ' ')).join(' / ');
  }, [location.pathname]);

  const handleThemeChange = (checked: boolean) => {
    const newTheme: ThemeMode = checked ? 'dark' : 'light';
    setTheme(newTheme);
  };

  const menuItems = useMemo<MenuProps['items']>(
    () => [
      {
        key: 'logout',
        label: 'Sign out',
        icon: <LogoutOutlined />,
        onClick: () => {
          signOut();
          navigate('/login', { replace: true });
        },
      },
    ],
    [navigate, signOut]
  );

  const initials = user?.username?.[0]?.toUpperCase() ?? 'U';

  return (
    <Layout.Header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#fff',
        padding: '0 24px',
        boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
        height: '64px',
        lineHeight: '64px',
        position: 'sticky',
        top: 0,
        zIndex: 10,
      }}
    >
      <Space size="large" align="center">
        <Button
          type="text"
          icon={isCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={toggleSidebar}
          style={{ fontSize: '18px' }}
        />
        <div style={{ display: 'flex', flexDirection: 'column', lineHeight: '1.4' }}>
          <Typography.Text type="secondary" style={{ fontSize: 12 }}>
            MTO360
          </Typography.Text>
          <Typography.Title level={4} style={{ margin: 0, textTransform: 'capitalize' }}>
            {pageTitle}
          </Typography.Title>
        </div>
      </Space>
      <Space size="large" align="center">
        <Space size="small" align="center">
          <SunOutlined style={{ color: theme === 'light' ? '#faad14' : undefined }} />
          <Switch
            checkedChildren={<MoonOutlined />}
            unCheckedChildren={<SunOutlined />}
            checked={theme === 'dark'}
            onChange={handleThemeChange}
          />
          <MoonOutlined style={{ color: theme === 'dark' ? '#722ed1' : undefined }} />
        </Space>
        <NotificationBell />
        <Dropdown menu={{ items: menuItems }} trigger={['click']}>
          <Space align="center" style={{ cursor: 'pointer' }}>
            <Avatar style={{ backgroundColor: '#1677ff' }}>{initials}</Avatar>
            <div style={{ lineHeight: '1.4' }}>
              <Typography.Text strong style={{ display: 'block' }}>
                {user?.username ?? 'User'}
              </Typography.Text>
              <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                {user?.email ?? 'user@example.com'}
              </Typography.Text>
            </div>
          </Space>
        </Dropdown>
      </Space>
    </Layout.Header>
  );
};

export default Header;

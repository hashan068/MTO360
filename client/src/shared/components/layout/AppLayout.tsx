import { Layout } from 'antd';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { useUIStore } from '@/shared/state/uiStore';

const { Sider, Content } = Layout;

const AppLayout = () => {
  const isCollapsed = useUIStore((state) => state.isSidebarCollapsed);
  const setSidebarCollapsed = useUIStore((state) => state.setSidebarCollapsed);

  return (
    <Layout style={{ minHeight: '100vh', height: '100vh', overflow: 'hidden' }}>
      <Sider
        collapsible
        collapsed={isCollapsed}
        onCollapse={setSidebarCollapsed}
        width={260}
        theme="dark"
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <Sidebar />
      </Sider>
      <Layout style={{ marginLeft: isCollapsed ? 80 : 260, transition: 'margin-left 0.2s' }}>
        <Header />
        <Content
          style={{
            margin: '24px',
            padding: '24px',
            minHeight: 280,
            background: '#fff',
            borderRadius: '8px',
            overflow: 'auto',
          }}
        >
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;

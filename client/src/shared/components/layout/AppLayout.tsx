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
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={isCollapsed}
        onCollapse={setSidebarCollapsed}
        width={260}
        theme="dark"
      >
        <Sidebar />
      </Sider>
      <Layout className="bg-slate-100">
        <Header />
        <Content className="p-6">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;

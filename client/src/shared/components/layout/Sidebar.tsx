import { DashboardOutlined, DatabaseOutlined, ShoppingCartOutlined, ToolOutlined } from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { Menu, Typography } from 'antd';
import { useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const menuItems: MenuProps['items'] = [
  {
    key: '/dashboard',
    icon: <DashboardOutlined />,
    label: 'Dashboard',
  },
  {
    key: '/inventory',
    icon: <DatabaseOutlined />,
    label: 'Inventory',
    children: [
      { key: '/inventory', label: 'Overview' },
      { key: '/inventory/components', label: 'Components' },
      { key: '/inventory/purchase-requisitions', label: 'Purchase Requisitions' },
      { key: '/inventory/purchase-orders', label: 'Purchase Orders' },
      { key: '/inventory/suppliers', label: 'Suppliers' },
      { key: '/inventory/reports', label: 'Reports' },
    ],
  },
  {
    key: '/sales',
    icon: <ShoppingCartOutlined />,
    label: 'Sales',
    children: [
      { key: '/sales', label: 'Overview' },
      { key: '/sales/customers', label: 'Customers' },
      { key: '/sales/products', label: 'Products' },
      { key: '/sales/rfqs', label: 'RFQs' },
      { key: '/sales/quotations', label: 'Quotations' },
      { key: '/sales/orders', label: 'Orders' },
    ],
  },
  {
    key: '/manufacturing',
    icon: <ToolOutlined />,
    label: 'Manufacturing',
    children: [
      { key: '/manufacturing', label: 'Overview' },
      { key: '/manufacturing/boms', label: 'BOMs' },
      { key: '/manufacturing/orders', label: 'Orders' },
      { key: '/manufacturing/material-requisitions', label: 'Material Reqs' },
    ],
  },
];

const findOpenKey = (path: string): string | undefined => {
  if (path.startsWith('/inventory')) return '/inventory';
  if (path.startsWith('/sales')) return '/sales';
  if (path.startsWith('/manufacturing')) return '/manufacturing';
  if (path.startsWith('/dashboard')) return '/dashboard';
  return undefined;
};

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const selectedKeys = useMemo(() => {
    const segments = location.pathname.split('/').filter(Boolean);
    if (segments.length === 0) {
      return ['/dashboard'];
    }
    const base = `/${segments.slice(0, Math.min(2, segments.length)).join('/')}`;
    return [base];
  }, [location.pathname]);

  const openKeys = useMemo(() => {
    const openKey = findOpenKey(location.pathname);
    return openKey ? [openKey] : [];
  }, [location.pathname]);

  const handleClick: MenuProps['onClick'] = ({ key }) => {
    navigate(key);
  };

  return (
    <div className="h-full flex flex-col">
      <div className="px-4 py-6">
        <Typography.Title level={4} style={{ color: 'white', margin: 0 }}>
          MTO360
        </Typography.Title>
        <Typography.Text style={{ color: 'rgba(255, 255, 255, 0.65)' }}>
          Operations Suite
        </Typography.Text>
      </div>
      <Menu
        key={openKeys.join('-') || 'root'}
        mode="inline"
        theme="dark"
        inlineCollapsed={false}
        onClick={handleClick}
        items={menuItems}
        selectedKeys={selectedKeys}
        defaultOpenKeys={openKeys}
      />
    </div>
  );
};

export default Sidebar;

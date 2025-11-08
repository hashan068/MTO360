import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Avatar from '@mui/material/Avatar';
import DashboardIcon from '@mui/icons-material/Dashboard';
import DescriptionIcon from '@mui/icons-material/Description';
import InventoryIcon from '@mui/icons-material/Inventory';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import BuildIcon from '@mui/icons-material/Build';
import WidgetsIcon from '@mui/icons-material/Widgets';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import AssignmentIcon from '@mui/icons-material/Assignment';
import AssessmentRoundedIcon from '@mui/icons-material/AssessmentRounded';
import logo from '../assets/logo.png';
import '../styles/drawer.css';
import { useNavigate } from 'react-router-dom';

const drawerWidth = 260;

// Salesperson, Production Manager, General Manager, Inventory Manager, Purchasing Manager, Admin

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/', roles: ['Admin', 'Salesperson', 'Production Manager', 'General Manager', 'Inventory Manager', 'Purchasing Manager'] },
  // { text: 'Insights', icon: <DashboardIcon />, path: '/sales/insights', roles: ['Admin', 'General Manager'] },
  {
    section: 'Sales',
    items: [
      { text: 'Quotations', icon: <DescriptionIcon />, path: '/sales/quotations', roles: ['Admin', 'Salesperson', 'General Manager'] },
      { text: 'Products', icon: <InventoryIcon />, path: '/sales/product', roles: ['Admin', 'Salesperson', 'General Manager'] },
      { text: 'Customers', icon: <InventoryIcon />, path: '/sales/customer', roles: ['Admin', 'Salesperson', 'General Manager'] },
      { text: 'Sales Orders', icon: <ShoppingCartIcon />, path: '/sales/salesorder', roles: ['Admin', 'Salesperson', 'General Manager', 'Production Manager'] },
    ],
  },
  {
    section: 'Manufacturing',
    items: [
      { text: 'Manufacturing Orders', icon: <BuildIcon />, path: '/mfg/mfgorder', roles: ['Admin', 'General Manager', 'Salesperson', 'Production Manager'] },
      { text: 'BOM', icon: <AccountTreeIcon />, path: '/mfg/bom', roles: ['Admin', 'General Manager', 'mfg', 'Production Manager'] },
    ],
  },
  {
    section: 'Inventory',
    items: [
      { text: 'Material Requisitions', icon: <AssignmentIcon />, path: '/mfg/materialreq', roles: ['Admin', 'General Manager', 'Inventory Manager', 'Production Manager'] },
      { text: 'Components', icon: <WidgetsIcon />, path: '/inventory/component', roles: ['Admin', 'Inventory Manager', 'Purchasing Manager'] },
      { text: 'Purchase Requisitions', icon: <LocalShippingIcon />, path: '/inventory/purchase-req', roles: ['Admin', 'General Manager', 'Inventory Manager', 'Purchasing Manager'] },
      { text: 'Purchase Orders', icon: <ShoppingCartIcon />, path: '/inventory/po', roles: ['Admin', 'General Manager', 'Inventory Manager', 'Purchasing Manager'] },
      { text: 'Suppliers', icon: <InventoryIcon />, path: '/inventory/suppliers', roles: ['Admin', 'General Manager', 'Purchasing Manager'] },
    ],
  },
  // {
  //   section: 'Notifications',
  //   items: [
  //     { text: 'Notifications', icon: <AssessmentRoundedIcon />, path: '/sales/sales-reports', roles: ['Admin', 'General Manager', 'Inventory Manager', 'Purchasing Manager'] },
  //   ],
  // },
  {
    section: 'Reports',
    items: [
      { text: 'Sales Report', icon: <AssessmentRoundedIcon />, path: '/sales/sales-reports', roles: ['Admin', 'General Manager', 'Salesperson'] },
      { text: 'Manufacturing Report', icon: <AssessmentRoundedIcon />, path: '/mfg/mfg-reports', roles: ['Admin', 'General Manager', 'Production Manager'] },
      { text: 'Inventory Report', icon: <AssessmentRoundedIcon />, path: '/inventory/inventory-reports', roles: ['Admin', 'General Manager', 'Inventory Manager', 'Purchasing Manager'] },
    ],
  },
];

export default function PermanentDrawerLeft() {
  const navigate = useNavigate();
  const [role, setRole] = React.useState(null);
  const [username, setUsername] = React.useState(null);

  React.useEffect(() => {
    const userRole = localStorage.getItem('userrole');
    const userName = localStorage.getItem('username');
    setRole(userRole);
    setUsername(userName);
  }, []);

  const handleNavigate = (path) => {
    navigate(path);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            backgroundColor: '#263238', // Dark background color for the drawer
            color: '#ffffff', // Text color for the drawer items
          },
        }}
        variant="permanent"
        anchor="left"
      >
        {/* Logo Container */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'left', py: 1, px: 3 }}>
          <img src={logo} alt="Logo" style={{ maxHeight: '48px', maxWidth: '100%' }} />
        </Box>
        <Divider sx={{ bgcolor: 'gray' }} />
        {/* Profile Container */}
        <Box sx={{ display: 'flex', alignItems: 'center', px: 3, py: 2 }}>
          <Avatar alt={username} src="/broken-image.jpg" />
          <Box sx={{ ml: 2 }}>
            <Typography variant="h6" component="div" style={{ fontSize: '22px' }}>
              {username}
            </Typography>
            <Typography variant="body2" component="div" style={{ fontSize: '14px' }}>
              {role}
            </Typography>

          </Box>
        </Box>
        <Divider sx={{ bgcolor: 'gray' }} />
        <List>
          {menuItems.map((item, index) => {
            if (item.section) {
              const visibleItems = item.items.filter(subItem => subItem.roles.includes(role));
              if (visibleItems.length > 0) {
                return (
                  <React.Fragment key={index}>
                    <Toolbar>
                      <Typography style={{ fontSize: '0.8rem' }} noWrap component="div">
                        {item.section}
                      </Typography>
                    </Toolbar>
                    <Divider sx={{ bgcolor: '#333333' }} />
                    {visibleItems.map((subItem, subIndex) => (
                      <ListItem key={subIndex} disablePadding onClick={() => handleNavigate(subItem.path)}>
                        <ListItemButton
                          sx={{
                            minHeight: '28px',
                            justifyContent: 'center',
                            '&:hover': {
                              backgroundColor: '#333333',
                            },
                          }}
                        >
                          <ListItemIcon sx={{ color: '#ffffff', fontSize: '8px' }}>{subItem.icon}</ListItemIcon>
                          <ListItemText primary={subItem.text} style={{ fontSize: '22px' }} />
                        </ListItemButton>
                      </ListItem>
                    ))}
                    <Divider sx={{ bgcolor: '#333333' }} />
                  </React.Fragment>
                );
              }
              return null;
            }
            if (item.roles.includes(role)) {
              return (
                <ListItem key={index} disablePadding onClick={() => handleNavigate(item.path)}>
                  <ListItemButton
                    sx={{
                      minHeight: '50px',
                      justifyContent: 'center',
                      '&:hover': {
                        backgroundColor: '#333333',
                      },
                    }}
                  >
                    <ListItemIcon sx={{ color: '#ffffff' }}>{item.icon}</ListItemIcon>
                    <ListItemText primary={item.text} />
                  </ListItemButton>
                  <Divider sx={{ bgcolor: '#333333' }} />
                </ListItem>
              );
            }
            return null;
          })}
        </List>
        <Divider sx={{ bgcolor: '#333333' }} />
      </Drawer>
    </Box>
  );
}

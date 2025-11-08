import React from 'react';
import { Box } from '@mui/material';
import PermanentDrawerLeft from './PermanentDrawerLeft';
import ResponsiveAppBar from './AppBar';

const Layout = ({ children }) => {
  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <PermanentDrawerLeft />
      <Box component="main" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <ResponsiveAppBar />
        <Box sx={{ flexGrow: 1, p: 2 }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default Layout;

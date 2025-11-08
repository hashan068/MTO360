import React from 'react';
import { AppBar, Toolbar, Button, Box } from '@mui/material';
import logo from '../../assets/logo.png';

const CustomAppBar = () => {
  return (
    <AppBar position="static" color="transparent" elevation={0}>
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Box
            component="img"
            src={logo}
            alt="Logo"
            sx={{ display: { xs: 'none', md: 'block' }, height: 60, mr: 2 }}
          />
        </Box>
        <Box>
          <Button color="inherit">Home</Button>
          <Button color="inherit">About</Button>
          <Button color="inherit">Services</Button>
          <Button color="inherit">Contact</Button>
          <Button variant="outlined" color="inherit">Login</Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default CustomAppBar;

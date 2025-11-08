// src/components/LoginLayout.js
import React from 'react';
import { Box, Paper, Typography, Container } from '@mui/material';
import CustomAppBar from './appbars/CustomAppBar';
import backgroundImage from '../assets/background.jpg';

const LoginLayout = ({ children }) => {
  return (
    <>
      <CustomAppBar />
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          backgroundImage: `url(${backgroundImage})`,
          backdropFilter: 'blur(2px)', // blur effect
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          padding: 2,
        }}
      >
        <Container maxWidth="xs">
          <Paper
            elevation={6}
            sx={{
              padding: 4,
              backgroundColor: 'rgba(255, 255, 255, 0.5)', // Slightly transparent white
              borderRadius: 2,
              backdropFilter: 'blur(10px)', // blur effect
            }}
          >
            <Typography variant="h6" align="center" gutterBottom>
              Login
            </Typography>
            {children}
          </Paper>
        </Container>
      </Box>
    </>
  );
};

export default LoginLayout;

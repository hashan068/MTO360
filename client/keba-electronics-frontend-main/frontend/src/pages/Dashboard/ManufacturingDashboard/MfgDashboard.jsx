import React from 'react';
import { Typography, Grid, Container, Box } from '@mui/material';
import MfgStatistics from './MfgStatistics';
import ProductionStatus from './ProductionStatus';
import RecentActivity from './RecentActivity';

const MfgDashboard = () => {
  return (
    <Box
      sx={{
        backgroundColor: '#cfd8dc',
        py: 1,
      }}
    >
      <Container maxWidth="lg" sx={{ py: 1 }}>
        <Typography variant="h5" align="center" gutterBottom>
          Manufacturing Dashboard
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <MfgStatistics />
          </Grid>
          <Grid item xs={12} md={6}>
            <ProductionStatus />
          </Grid>
          <Grid item xs={12} md={6}>
            <RecentActivity />
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default MfgDashboard;

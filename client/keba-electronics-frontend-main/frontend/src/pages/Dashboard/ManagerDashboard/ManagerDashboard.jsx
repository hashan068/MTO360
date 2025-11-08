import React from 'react';
import { Typography, Grid, Container } from '@mui/material';
import SalesChart from './../SalesChart';
import TopSellingProducts from './../TopSellingProducts';
import TopCustomers from './../TopCustomers';
import StatisticsDashboard from './../StatisticsDashboard';

export default function ManagerDashboard() {
  return (
    <Container maxWidth="lg" sx={{ py: 1 }}>
      <Typography variant="h5" align="center" gutterBottom>
        Manager Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <StatisticsDashboard />
        </Grid>
        <Grid item xs={12} >
          <SalesChart />
        </Grid>
        <Grid item xs={12} md={6}>
          <TopSellingProducts />
        </Grid>
        <Grid item xs={12} md={6}>
          <TopCustomers />
        </Grid>
      </Grid>
    </Container>
  );
}

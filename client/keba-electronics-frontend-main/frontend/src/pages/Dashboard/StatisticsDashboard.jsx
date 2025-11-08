import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box, CircularProgress } from '@mui/material';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import PeopleIcon from '@mui/icons-material/People';
import InventoryIcon from '@mui/icons-material/Inventory';
import ReceiptIcon from '@mui/icons-material/Receipt';
import api from '../../api';

const StatisticsDashboard = () => {
  const [data, setData] = useState([
    { label: 'Quotations', value: 0, icon: <ReceiptIcon />, color: '#4caf50'},
    { label: 'Sales Orders', value: 0, icon: <ShoppingCartIcon />, color: '#ff9800'},
    { label: 'Customers', value: 0, icon: <PeopleIcon />, color: '#2196f3'},
    { label: 'Products', value: 0, icon: <InventoryIcon />, color: '#9c27b0'},
  ]);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCustomers = api.get('/api/sales/customers/');
    const fetchOrders = api.get('/api/sales/orders/');
    const fetchQuotations = api.get('/api/sales/quotations/');
    const fetchProducts = api.get('/api/sales/products/');

    Promise.all([fetchCustomers, fetchOrders, fetchQuotations, fetchProducts])
      .then(([customersResponse, ordersResponse, quotationsResponse, productsResponse]) => {
        const customers = customersResponse.data.length;
        const pendingQuotations = quotationsResponse.data.filter(quotation => quotation.status === 'pending').length;
        const pendingOrders = ordersResponse.data.filter(order => order.status === 'pending').length;
        const products = productsResponse.data.length;

        setData(prevData => prevData.map(item => {
          if (item.label === 'Customers') return { ...item, value: customers };
          if (item.label === 'Sales Orders') return { ...item, value: pendingOrders };
          if (item.label === 'Quotations') return { ...item, value: pendingQuotations };
          if (item.label === 'Products') return { ...item, value: products };
          return item;
        }));
        setLoading(false);
      })
      .catch(error => {
        console.error('There was an error fetching the data!', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  return (
    <Box sx={{ flexGrow: 1, padding: '20px' }}>
      <Grid container spacing={3}>
        {data.map((item, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Paper elevation={3} sx={{ padding: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center', backgroundColor: item.color }}>
              <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
                <Box sx={{ marginRight: '10px' }}>{item.icon}</Box>
                <Typography variant="h4">{item.value}</Typography>
              </Box>

              <Typography variant="subtitle1">{item.label}</Typography>

            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default StatisticsDashboard;
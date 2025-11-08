// InventoryStatistics.jsx
import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box, CircularProgress } from '@mui/material';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import PeopleIcon from '@mui/icons-material/People';
import InventoryIcon from '@mui/icons-material/Inventory';
import ReceiptIcon from '@mui/icons-material/Receipt';
import api from '../../../api';


const InventoryStatistics = () => {
  const [data, setData] = useState([
    { label: 'Components', value: 0, icon: <InventoryIcon />, color: '#4caf50'},
    { label: 'Purchase Requisitions', value: 0, icon: <ReceiptIcon />, color: '#ff9800'},
    { label: 'Suppliers', value: 0, icon: <PeopleIcon />, color: '#2196f3'},
    { label: 'Purchase Orders', value: 0, icon: <ShoppingCartIcon />, color: '#9c27b0'},
  ]);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchComponents = api.get('/api/inventory/components/');
    const fetchPurchaseRequisitions = api.get('/api/inventory/purchase-requisitions/');
    const fetchSuppliers = api.get('/api/inventory/suppliers/');
    const fetchPurchaseOrders = api.get('/api/inventory/purchase-orders/');

    Promise.all([fetchComponents, fetchPurchaseRequisitions, fetchSuppliers, fetchPurchaseOrders])
      .then(([componentsResponse, purchaseRequisitionsResponse, suppliersResponse, purchaseOrdersResponse]) => {
        const components = componentsResponse.data.length;
        const pendingPurchaseRequisitions = purchaseRequisitionsResponse.data.filter(req => req.status === 'pending').length;
        const suppliers = suppliersResponse.data.length;
        const pendingPurchaseOrders = purchaseOrdersResponse.data.filter(order => order.status === 'draft').length;

        setData(prevData => prevData.map(item => {
          if (item.label === 'Components') return { ...item, value: components };
          if (item.label === 'Purchase Requisitions') return { ...item, value: pendingPurchaseRequisitions };
          if (item.label === 'Suppliers') return { ...item, value: suppliers };
          if (item.label === 'Purchase Orders') return { ...item, value: pendingPurchaseOrders };
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
    <Box sx={{ flexGrow: 1, padding: '10px' }}>
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

export default InventoryStatistics;

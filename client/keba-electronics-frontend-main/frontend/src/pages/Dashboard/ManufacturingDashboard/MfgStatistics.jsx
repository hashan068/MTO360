import React, { useState, useEffect } from 'react';
import { Grid, Paper, Typography, Box, CircularProgress } from '@mui/material';
import BuildIcon from '@mui/icons-material/Build';
import PlaylistAddCheckIcon from '@mui/icons-material/PlaylistAddCheck';
import DescriptionIcon from '@mui/icons-material/Description';
import ListAltIcon from '@mui/icons-material/ListAlt';
import api from '../../../api';

const MfgStatistics = () => {
  const [data, setData] = useState([
    { label: 'Manufacturing Orders', value: 0, icon: <BuildIcon />, color: '#4caf50'},
    { label: 'Material Requisitions', value: 0, icon: <PlaylistAddCheckIcon />, color: '#ff9800'},
    { label: 'Bills of Material', value: 0, icon: <DescriptionIcon />, color: '#2196f3'},
    { label: 'BOM Items', value: 0, icon: <ListAltIcon />, color: '#9c27b0'},
  ]);

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchManufacturingOrders = api.get('/api/manufacturing/manufacturing-orders/');
    const fetchMaterialRequisitions = api.get('/api/manufacturing/material-requisitions/');
    const fetchBillsOfMaterial = api.get('/api/manufacturing/bills-of-material/');
    const fetchBomItems = api.get('/api/manufacturing/bom-items/');

    Promise.all([fetchManufacturingOrders, fetchMaterialRequisitions, fetchBillsOfMaterial, fetchBomItems])
      .then(([manufacturingOrdersResponse, materialRequisitionsResponse, billsOfMaterialResponse, bomItemsResponse]) => {
        const manufacturingOrders = manufacturingOrdersResponse.data.length;
        const pendingMaterialRequisitions = materialRequisitionsResponse.data.filter(req => req.status === 'pending').length;
        const billsOfMaterial = billsOfMaterialResponse.data.length;
        const bomItems = bomItemsResponse.data.length;

        setData(prevData => prevData.map(item => {
          if (item.label === 'Manufacturing Orders') return { ...item, value: manufacturingOrders };
          if (item.label === 'Material Requisitions') return { ...item, value: pendingMaterialRequisitions };
          if (item.label === 'Bills of Material') return { ...item, value: billsOfMaterial };
          if (item.label === 'BOM Items') return { ...item, value: bomItems };
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

export default MfgStatistics;
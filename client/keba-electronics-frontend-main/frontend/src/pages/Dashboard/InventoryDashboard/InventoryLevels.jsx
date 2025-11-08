import React, { useEffect, useState } from'react';
import { Grid, Card, CardContent, Typography } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from'recharts';
import api from '../../../api';

const InventoryLevels = () => {
  const [components, setComponents] = useState([]);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    api.get('/api/inventory/components/')
    .then(response => {
        setComponents(response.data);
        const chartData = response.data.map(component => ({
          name: component.name,
          quantity: component.quantity,
          reorderLevel: component.reorder_quantity,
        }));
        setChartData(chartData);
      })
    .catch(error => {
        console.error('Error fetching components:', error);
      });
  }, []);

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Inventory Levels
            </Typography>
            <BarChart width={1000} height={400} data={chartData}>
              <CartesianGrid stroke="#ccc" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="quantity" fill="#8884d8" />
              <Bar dataKey="reorderLevel" fill="#82ca9d" />
            </BarChart>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default InventoryLevels;
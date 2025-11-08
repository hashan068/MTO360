import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Paper, Box, Typography, CircularProgress } from '@mui/material';
import api from '../../../api';

const COLORS = ['#4caf50', '#ff9800', '#2196f3', '#9c27b0', '#f44336', '#795548'];

// Mapping of API status values to user-friendly names
const STATUS_CHOICES = {
  'pending': 'Pending',
  'mr_sent': 'MR Sent',
  'mr_approved': 'MR Approved',
  'mr_rejected': 'MR Rejected',
  'in_production': 'In Production',
  'completed': 'Completed',
  'cancelled': 'Cancelled'
};

const ProductionStatus = () => {
  const [statusData, setStatusData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get('/api/manufacturing/manufacturing-orders/')
      .then(response => {
        const rawOrders = response.data;
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        const recentOrders = rawOrders.filter(order => new Date(order.updated_at) >= thirtyDaysAgo);
        const statusCounts = recentOrders.reduce((acc, order) => {
          acc[order.status] = (acc[order.status] || 0) + 1;
          return acc;
        }, {});
        const formattedData = Object.entries(statusCounts).map(([status, count]) => ({
          status: STATUS_CHOICES[status] || status, // Use user-friendly name or default to the original status
          count
        }));
        setStatusData(formattedData);
        setLoading(false);
      })
      .catch(error => {
        setError('There was an error fetching the data!');
        console.error('There was an error fetching the data!', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <Paper elevation={3} sx={{ padding: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <Typography variant="h6" gutterBottom>
        Production Status
      </Typography>
      <ResponsiveContainer width="100%" height={400}>
        <PieChart>
          <Pie
            data={statusData}
            dataKey="count"
            nameKey="status"
            cx="50%"
            cy="50%"
            outerRadius={150}
            fill="#8884d8"
            label={({ status }) => status}
          >
            {statusData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Paper>
  );
};

export default ProductionStatus;

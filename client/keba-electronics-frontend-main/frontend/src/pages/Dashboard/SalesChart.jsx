import React, { useState, useEffect } from 'react';
import { Paper, Typography, Box, CircularProgress, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../../api';
import dayjs from 'dayjs';

const SalesChart = () => {
  const [salesData, setSalesData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterOption, setFilterOption] = useState('last30Days');

  const formatDate = (date) => dayjs(date).format('MM-DD');

  const getDateRange = (option) => {
    const today = dayjs();
    switch (option) {
      case 'last7Days':
        return {
          start: today.subtract(6, 'days').format('YYYY-MM-DD'),
          end: today.format('YYYY-MM-DD'),
        };
      case 'last30Days':
        return {
          start: today.subtract(29, 'days').format('YYYY-MM-DD'),
          end: today.format('YYYY-MM-DD'),
        };
      default:
        return undefined;
    }
  };

  const getSalesData = async () => {
    setLoading(true);
    try {
      const dateRange = getDateRange(filterOption);
      const params = dateRange
        ? {
            start_date: dateRange.start,
            end_date: dateRange.end,
          }
        : {};

      const res = await api.get('/api/sales/orders/', { params });
      const transformedData = res.data.flatMap((order) =>
        order.order_items.map((item) => ({
          date: formatDate(dayjs(order.created_at_date).toDate()),
          sales: parseFloat(item.price) * item.quantity,
        }))
      );

      // Group data by date and sum sales for each day
      const groupedData = transformedData.reduce((acc, current) => {
        const existingDate = acc.find((item) => item.date === current.date);
        if (existingDate) {
          existingDate.sales += current.sales;
        } else {
          acc.push(current);
        }
        return acc;
      }, []);

      // Sort data by date
      const sortedData = groupedData.sort((a, b) => dayjs(a.date, 'MM-DD').diff(dayjs(b.date, 'MM-DD')));
      setSalesData(sortedData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    getSalesData();
  }, [filterOption]);

  // Format sales value to display in thousands (k)
  const formatSalesValue = (value) => `${(value / 1000).toFixed(1)}k`;

  return (
    <Paper sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Sales Over Time</Typography>
        <FormControl>
          <InputLabel id="filter-label">Filter</InputLabel>
          <Select
            labelId="filter-label"
            value={filterOption}
            onChange={(e) => setFilterOption(e.target.value)}
            label="Filter"
          >
            <MenuItem value="last30Days">Last 30 Days</MenuItem>
            <MenuItem value="last7Days">Last 7 Days</MenuItem>
          </Select>
        </FormControl>
      </Box>
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={salesData} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
            <XAxis dataKey="date" />
            <YAxis tickFormatter={formatSalesValue} />
            <CartesianGrid strokeDasharray="3 3" />
            <Tooltip formatter={(value) => formatSalesValue(value)} />
            <Legend />
            <Line type="monotone" dataKey="sales" stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>
      )}
    </Paper>
  );
};

export default SalesChart;
// TopCustomers.jsx
import React, { useState, useEffect } from 'react';
import { Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TableSortLabel } from '@mui/material';
import api from '../../api';

const TopCustomers = () => {
  const [topCustomers, setTopCustomers] = useState([]);
  const [order, setOrder] = useState('desc');
  const [orderBy, setOrderBy] = useState('total_amount');

  useEffect(() => {
    const fetchTopCustomers = async () => {
      try {
        const ordersResponse = await api.get('/api/sales/orders/');
        const orders = ordersResponse.data;

        const customerCounts = orders.reduce((counts, order) => {
          const { customer, customer_name, total_amount } = order;
          if (counts[customer]) {
            counts[customer].total_amount += parseFloat(total_amount);
          } else {
            counts[customer] = { customer, customer_name, total_amount: parseFloat(total_amount) };
          }
          return counts;
        }, {});

        const sortedCustomers = Object.values(customerCounts).sort((a, b) => {
          const orderMultiplier = order === 'asc' ? 1 : -1;
          if (a[orderBy] < b[orderBy]) return -1 * orderMultiplier;
          if (a[orderBy] > b[orderBy]) return 1 * orderMultiplier;
          return 0;
        });
        setTopCustomers(sortedCustomers.slice(0, 5));
      } catch (error) {
        console.error('Error fetching top customers:', error);
      }
    };

    fetchTopCustomers();
  }, [order, orderBy]);

  const handleSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Top Customers
      </Typography>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'customer_name'}
                  direction={orderBy === 'customer_name' ? order : 'asc'}
                  onClick={() => handleSort('customer_name')}
                >
                  Customer
                </TableSortLabel>
              </TableCell>
              <TableCell align="right">
                <TableSortLabel
                  active={orderBy === 'total_amount'}
                  direction={orderBy === 'total_amount' ? order : 'asc'}
                  onClick={() => handleSort('total_amount')}
                >
                  Total Sales
                </TableSortLabel>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {topCustomers.map((customer) => (
              <TableRow key={customer.customer}>
                <TableCell>{customer.customer_name}</TableCell>
                <TableCell align="right">{customer.total_amount.toFixed(2)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default TopCustomers;
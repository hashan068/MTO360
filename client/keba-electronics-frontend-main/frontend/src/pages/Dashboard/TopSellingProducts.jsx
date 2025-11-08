// TopSellingProducts.jsx
import React, { useState, useEffect } from 'react';
import { Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TableSortLabel } from '@mui/material';
import api from '../../api';

const TopSellingProducts = () => {
  const [topProducts, setTopProducts] = useState([]);
  const [order, setOrder] = useState('desc');
  const [orderBy, setOrderBy] = useState('quantity');

  useEffect(() => {
    const fetchTopProducts = async () => {
      try {
        const orderItemsResponse = await api.get('/api/sales/order-items/');
        const orderItems = orderItemsResponse.data;

        const productCounts = orderItems.reduce((counts, item) => {
          const { product, quantity } = item;
          if (counts[product]) {
            counts[product].quantity += quantity;
          } else {
            counts[product] = { ...item, quantity };
          }
          return counts;
        }, {});

        const sortedProducts = Object.values(productCounts).sort((a, b) => {
          const orderMultiplier = order === 'asc' ? 1 : -1;
          if (a[orderBy] < b[orderBy]) return -1 * orderMultiplier;
          if (a[orderBy] > b[orderBy]) return 1 * orderMultiplier;
          return 0;
        });
        setTopProducts(sortedProducts);
      } catch (error) {
        console.error('Error fetching top-selling products:', error);
      }
    };

    fetchTopProducts();
  }, [order, orderBy]);

  const handleSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Top-Selling Products
      </Typography>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>
                <TableSortLabel
                  active={orderBy === 'product_name'}
                  direction={orderBy === 'product_name' ? order : 'asc'}
                  onClick={() => handleSort('product_name')}
                >
                  Product
                </TableSortLabel>
              </TableCell>
              <TableCell align="right">
                <TableSortLabel
                  active={orderBy === 'quantity'}
                  direction={orderBy === 'quantity' ? order : 'asc'}
                  onClick={() => handleSort('quantity')}
                >
                  Total Quantity
                </TableSortLabel>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {topProducts.map((product) => (
              <TableRow key={product.product}>
                <TableCell>{product.product_name}</TableCell>
                <TableCell align="right">{product.quantity}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};

export default TopSellingProducts;
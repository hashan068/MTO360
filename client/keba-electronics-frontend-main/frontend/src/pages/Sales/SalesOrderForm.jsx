import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import Alert from '@mui/material/Alert';
import { Autocomplete, TextField } from '@mui/material';

const SalesOrderForm = () => {
  const [customer, setCustomer] = useState(null);
  const [product, setProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [salesOrderItems, setSalesOrderItems] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [alert, setAlert] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const customersResponse = await fetch('http://127.0.0.1:8000/api/sales/customers/');
        const customersData = await customersResponse.json();
        setCustomers(customersData);

        const productsResponse = await fetch('http://127.0.0.1:8000/api/sales/products/');
        const productsData = await productsResponse.json();
        setProducts(productsData);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  const handleAddItem = () => {
    if (product && quantity > 0) {
      const newItem = {
        product,
        quantity,
        price: product.price,
      };

      setSalesOrderItems([...salesOrderItems, newItem]);
      setQuantity(1);
      setProduct(null);
    }
  };

  const validateForm = () => {
    if (!customer) {
      alert('Please select a customer.');
      return false;
    }

    if (salesOrderItems.length === 0) {
      alert('Please add at least one item to the order.');
      return false;
    }

    return true;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
  
    if (!validateForm()) {
      return;
    }
  
    const salesOrderData = {
      customer: customer.id,
      order_items: salesOrderItems.map((item) => ({
        product: item.product.id,
        quantity: item.quantity,
        price: item.price,
      })),
    };
  
    console.log('Sending data:', salesOrderData); // Log the data being sent
  
    try {
      const response = await fetch('http://127.0.0.1:8000/api/sales/orders/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(salesOrderData),
      });
  
      const responseData = await response.json();
  
      console.log('Received data:', responseData); // Log the response data
  
      if (response.ok) {
        // alert('Sales order created successfully!');
        setAlert({ severity: 'success', message: 'This is a success Alert.' });
        setTimeout(() => {
          setAlert(null);
        }, 3000); // Hide the alert after 3 seconds
        setCustomer(null);
        setSalesOrderItems([]);
      } else {
        alert(`Error creating sales order: ${responseData.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error creating sales order:', error);
      alert('An error occurred while creating the sales order. Please try again later.');
    }
  };
  

  const handleDeleteItem = (index) => {
    const updatedSalesOrderItems = [...salesOrderItems];
    updatedSalesOrderItems.splice(index, 1);
    setSalesOrderItems(updatedSalesOrderItems);
  };

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom>
        Sales Order Form
      </Typography>
      <form onSubmit={handleSubmit}>
        <Autocomplete
          options={customers}
          value={customer}
          onChange={(event, newValue) => setCustomer(newValue)}
          getOptionLabel={(option) => option.name}
          renderInput={(params) => <TextField {...params} label="Customer" fullWidth margin="normal" />}
        />
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Product</TableCell>
                <TableCell align="right">Quantity</TableCell>
                <TableCell align="right">Price</TableCell>
                <TableCell align="right">Total</TableCell>
                <TableCell align="right">Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {salesOrderItems.map((item, index) => (
                <TableRow key={index}>
                  <TableCell>{item.product.name}</TableCell>
                  <TableCell align="right">{item.quantity}</TableCell>
                  <TableCell align="right">{item.price}</TableCell>
                  <TableCell align="right">{item.quantity * item.price}</TableCell>
                  <TableCell align="right">
                    <Button variant="contained" color="error" onClick={() => handleDeleteItem(index)}>
                      Delete
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
          <Autocomplete
            options={products}
            value={product}
            onChange={(event, newValue) => setProduct(newValue)}
            getOptionLabel={(option) => option.name}
            renderOption={(props, option) => (
              <li {...props} key={option.id}> {/* Use option.id instead of option.name as the key */}
                {option.name}
              </li>
            )}
            renderInput={(params) => <TextField {...params} label="Product" margin="normal" />}
            sx={{ width: '50%' }}
          />
          <TextField
            type="number"
            value={quantity}
            onChange={(event) => setQuantity(event.target.value)}
            label="Quantity"
            margin="normal"
            sx={{ ml: 2, mr: 2, width: '300px' }}
          />
          <Button variant="contained" onClick={handleAddItem}>
            Add Item
          </Button>
        </Box>

        <Button type="submit" variant="contained" color="primary" sx={{ mt: 2 }}>
          Submit Order
        </Button>
      </form>
      <div>
      {alert && <Alert severity={alert.severity}>{alert.message}</Alert>}
      {/* Rest of the component JSX */}
    </div>
    </Box>
  );
};

export default SalesOrderForm;

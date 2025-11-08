import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Grid,
  IconButton,
  Container,
  Autocomplete,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Snackbar,
  Alert,
} from '@mui/material';
import { styled } from '@mui/system';

const StyledContainer = styled(Container)(({ theme }) => ({
  padding: theme.spacing(4),
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[2],
}));

const StyledForm = styled('form')(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(3),
}));

const StyledTableContainer = styled(TableContainer)(({ theme }) => ({
  marginTop: theme.spacing(3),
}));

const StyledButton = styled(Button)(({ theme }) => ({
  marginTop: theme.spacing(3),
  alignSelf: 'center',
  padding: theme.spacing(1.5, 4),
}));

const AddBOMForm = () => {
  const [bomName, setBomName] = useState('');
  const [product, setProduct] = useState(null);
  const [bomItems, setBomItems] = useState([]);
  const [products, setProducts] = useState([]);
  const [components, setComponents] = useState([]);
  const [alert, setAlert] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [item, setItem] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [productsData, componentsData] = await Promise.all([
          fetch('http://127.0.0.1:8000/api/sales/products/').then((res) => res.json()),
          fetch('http://127.0.0.1:8000/api/inventory/components/').then((res) => res.json()),
        ]);

        setProducts(
          productsData.map((product) => ({
            id: product.id,
            name: product.product_name,
            description: product.description,
            price: parseFloat(product.price),
            bom: product.bom,
          }))
        );
        setComponents(componentsData);
      } catch (error) {
        console.error('Error fetching data:', error);
        setAlert({ severity: 'error', message: 'An error occurred while fetching data. Please try again later.' });
      }
    };

    fetchData();
  }, []);

  const handleAddItem = () => {
    if (item && quantity > 0) {
      const newItem = {
        component: item,
        quantity,
      };

      setBomItems([...bomItems, newItem]);
      setQuantity(1);
      setItem(null);
    }
  };

  const handleProductChange = (event, newValue) => {
    setProduct(newValue);
  };

  const handleBomItemChange = (event, newValue) => {
    setItem(newValue);
  };

  const handleDeleteItem = (itemToDelete) => {
    const updatedBomItems = bomItems.filter((item) => item !== itemToDelete);
    setBomItems(updatedBomItems);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    // Check if at least one BOM item is present
    if (bomItems.length === 0) {
      setAlert({ severity: 'error', message: 'At least one BOM item is required.' });
      return;
    }

    const bomData = {
      name: bomName,
      product: product.id,
      bom_items: bomItems.map((item) => ({
        component: item.component.id,
        quantity: item.quantity,
      })),
    };

    try {
      const response = await fetch('http://127.0.0.1:8000/api/manufacturing/bills-of-material/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bomData),

      });
      const responseData = await response.json();

      if (response.ok) {
        setAlert({ severity: 'success', message: 'BOM Created Successfully!' });
        setBomName('');
        setProduct(null);
        setBomItems([]);
      } else {
        setAlert({ severity: 'error', message: `Error creating BOM: ${responseData.error || 'Unknown error'}` });
      }
    } catch (error) {
      console.error('Error creating BOM:', error);
      setAlert({ severity: 'error', message: 'An error occurred while creating the BOM. Please try again later.' });
    }
  };

  return (
    <StyledContainer maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Add BOM
      </Typography>
      <StyledForm onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              label="BOM Name"
              value={bomName}
              onChange={(event) => setBomName(event.target.value)}
              required
              fullWidth
            />
          </Grid>
          <Grid item xs={12}>
            <Autocomplete
              options={products}
              value={product}
              onChange={handleProductChange}
              getOptionLabel={(option) => option.name}
              renderOption={(props, option) => (
                <li {...props} key={option.id}>
                  {option.name}
                </li>
              )}
              renderInput={(params) => <TextField {...params} label="Product" margin="normal" />}
              sx={{ width: '50%' }}
              isOptionEqualToValue={(option, value) => option.id === value.id} // Add this line
            />

          </Grid>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Autocomplete
                options={components}
                value={item}
                onChange={handleBomItemChange}
                getOptionLabel={(option) => option.name || ''}
                renderInput={(params) => <TextField {...params} label="Component" />}
                isOptionEqualToValue={(option, value) => option.id === value.id}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                type="number"
                value={quantity}
                onChange={(event) => setQuantity(event.target.value)}
                label="Quantity"
                fullWidth
              />
            </Grid>

            <Grid item xs={12} md={3}>
              <Button variant="contained" onClick={handleAddItem} fullWidth>
                Add Item
              </Button>
            </Grid>
          </Grid>

          <Grid item xs={12}>
            <StyledTableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Component</TableCell>
                    <TableCell align="right">Quantity</TableCell>
                    <TableCell align="right">Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {bomItems.map((item, index) => (
                    <TableRow key={`${item.component.id}-${item.quantity}`}>
                      <TableCell>{item.component.name}</TableCell>
                      <TableCell align="right">{item.quantity}</TableCell>
                      <TableCell align="right">
                        <Button
                          variant="contained"
                          color="error"
                          onClick={() => handleDeleteItem(item)}
                        >
                          Delete
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </StyledTableContainer>
          </Grid>

          <Grid item xs={12}>
            <StyledButton type="submit" variant="contained" color="primary">
              Create BOM
            </StyledButton>
          </Grid>
        </Grid>
      </StyledForm>

      <Snackbar
        open={!!alert}
        autoHideDuration={3000}
        onClose={() => setAlert(null)}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert onClose={() => setAlert(null)} severity={alert?.severity}>
          {alert?.message}
        </Alert>
      </Snackbar>
    </StyledContainer>
  );
};

export default AddBOMForm;
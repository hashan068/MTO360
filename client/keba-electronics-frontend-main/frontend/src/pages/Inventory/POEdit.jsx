import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  TextField,
  Grid,
  ThemeProvider,
  createTheme,
  Stack,
  Autocomplete,
  MenuItem, // Import MenuItem from @mui/material
} from '@mui/material';
import api from '../../api';

const theme = createTheme({
  palette: {
    primary: { main: '#6200ea' },
    secondary: { main: '#03dac6' },
  },
  typography: { h4: { fontWeight: 600 } },
  components: {
    MuiTextField: { styleOverrides: { root: { borderRadius: 8 } } },
    MuiButton: { styleOverrides: { root: { borderRadius: 8 } } },
  },
});

const POEdit = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [initialValues, setInitialValues] = useState({
    purchase_requisition: null,
    component: null,
    quantity: 'N/A',
    notes: '',
    priority: 'high', // Set default priority to 'high'
    purchase_manager_approval: false,
    status: 'draft',
    supplier: null,
  });

  const [suppliers, setSuppliers] = useState([]);
  const [supplier, setSupplier] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const supplierResponse = await api.get('/api/inventory/suppliers/');
        setSuppliers(supplierResponse.data);

        if (id) {
          const response = await api.get(`/api/inventory/purchase-orders/${id}/`);
          const {
            purchase_requisition,
            component,
            quantity,
            notes,
            priority,

            status,
            supplier: initialSupplier,
          } = response.data;
          setInitialValues({
            purchase_requisition,
            component,
            quantity,
            notes,
            priority,

            status,
            supplier: initialSupplier,
          });
          setSupplier(initialSupplier);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [id]);

  const handleSupplierChange = (event, newValue) => {
    setSupplier(newValue);
  };

  const handleNotesChange = (event) => {
    setInitialValues({ ...initialValues, notes: event.target.value });
  };

  const handleSubmit = async () => {
    try {
      const data = {
        supplier_id: supplier ? supplier.id : null,
        notes: initialValues.notes,
      };

      if (id) {
        await api.put(`/api/inventory/purchase-orders/${id}/`, data);
      } else {
        await api.post('/api/inventory/purchase-orders/', data);
      }

      navigate(-1);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ p: 4, bgcolor: 'background.paper', boxShadow: 3, borderRadius: 2 }}>
        <Typography variant="h4" gutterBottom>
          {id ? 'Edit Purchase Order' : 'Create Purchase Order'}
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="body1">
              Component: {initialValues.component ? initialValues.component.name : 'N/A'}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <TextField
              label="Quantity"
              value={initialValues.quantity}
              InputProps={{
                readOnly: true,
              }}
              fullWidth
              required
            />
          </Grid>
          <Grid item xs={12}>
            <Typography variant="body1">
              Purchase Requisition: {initialValues.purchase_requisition ? initialValues.purchase_requisition.id : 'N/A'}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <TextField
              label="Notes"
              value={initialValues.notes}
              onChange={handleNotesChange}
              fullWidth
              multiline
              rows={4}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              label="Priority"
              value={initialValues.priority}
              InputProps={{
                readOnly: true,
              }}
              fullWidth
              select
            >
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="low">Low</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12}>
            <Autocomplete
              options={suppliers}
              value={supplier}
              onChange={handleSupplierChange}
              getOptionLabel={(option) => option.name || ''}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Supplier"
                />
              )}
              isOptionEqualToValue={(option, value) => option?.id === value?.id}
            />
          </Grid>
        </Grid>
        <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
          <Button variant="contained" color="secondary" onClick={() => navigate(-1)} sx={{ flexGrow: 1 }}>
            Back
          </Button>
          <Button
            type="button"
            variant="contained"
            color="primary"
            onClick={handleSubmit}
          >
            Save
          </Button>
        </Stack>
      </Box>
    </ThemeProvider>
  );
};

export default POEdit;

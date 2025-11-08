import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Alert,
  Container,
  Paper,
  Grid,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import api from '../../api';

// Validation schema using Yup
const validationSchema = Yup.object({
  description: Yup.string().required('Description is required'),
  price: Yup.number().required('Price is required').min(0, 'Price must be a positive value'),
  inverter_type: Yup.string().required('Inverter type is required'),
  power_rating: Yup.number().required('Power rating is required').min(1, 'Power rating must be greater than 0'),
  frequency: Yup.number().required('Frequency is required').min(0, 'Frequency must be a positive value'),
  efficiency: Yup.number().required('Efficiency is required').min(0, 'Efficiency must be a positive value').max(100, 'Efficiency must be less than or equal to 100'),
  surge_power: Yup.number().required('Surge power is required').min(1, 'Surge power must be greater than 0'),
  warranty_years: Yup.number().required('Warranty years is required').min(0, 'Warranty years must be a non-negative value'),
  input_voltage: Yup.number().required('Input voltage is required').min(0, 'Input voltage must be a positive value'),
  output_voltage: Yup.number().required('Output voltage is required').min(0, 'Output voltage must be a positive value'),
});

const ProductForm = () => {
  const navigate = useNavigate();
  const [alert, setAlert] = useState(null);
  const [open, setOpen] = useState(false);
  const [alertDialogOpen, setAlertDialogOpen] = useState(false);

  const formik = useFormik({
    initialValues: {
      description: '',
      price: '',
      inverter_type: '',
      power_rating: '',
      frequency: '',
      efficiency: '',
      surge_power: '',
      warranty_years: '',
      input_voltage: '',
      output_voltage: '',
    },
    validationSchema: validationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      setOpen(false); // Close confirmation dialog
      try {
        const response = await api.post('/api/sales/products/', values);

        if (response.status === 201) {
          setAlert({ severity: 'success', message: 'Product created successfully.' });
          formik.resetForm();
          setAlertDialogOpen(true);
          setTimeout(() => {
            setAlertDialogOpen(false);
            navigate('/sales/product'); // Redirect to product page after 3 seconds
          }, 3000);
        } else {
          setAlert({ severity: 'error', message: `Error creating product: ${response.data}` });
          setAlertDialogOpen(true);
        }
      } catch (error) {
        console.error('Fetch Error:', error);
        setAlert({ severity: 'error', message: 'An error occurred while creating the product.' });
        setAlertDialogOpen(true);
      } finally {
        setSubmitting(false);
      }
    },
  });

  const handleDialogOpen = () => {
    setOpen(true);
  };

  const handleDialogClose = () => {
    setOpen(false);
  };

  const handleAlertDialogClose = () => {
    setAlertDialogOpen(false);
  };
  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" gutterBottom align="center">
          Product Form
        </Typography>
        <form onSubmit={formik.handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                label="Description"
                name="description"
                value={formik.values.description}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.description && Boolean(formik.errors.description)}
                helperText={formik.touched.description && formik.errors.description}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Price"
                name="price"
                type="number"
                value={formik.values.price}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.price && Boolean(formik.errors.price)}
                helperText={formik.touched.price && formik.errors.price}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel id="inverter-type-label">Inverter Type</InputLabel>
                <Select
                  labelId="inverter-type-label"
                  id="inverter-type"
                  name="inverter_type"
                  value={formik.values.inverter_type}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  error={formik.touched.inverter_type && Boolean(formik.errors.inverter_type)}
                >
                  <MenuItem value="">Select Inverter Type</MenuItem>
                  <MenuItem value="Pure Sine Wave">Pure Sine Wave</MenuItem>
                  <MenuItem value="Modified Sine Wave">Modified Sine Wave</MenuItem>
                  <MenuItem value="Square Wave">Square Wave</MenuItem>
                </Select>
                {formik.touched.inverter_type && formik.errors.inverter_type && (
                  <Typography variant="caption" color="error">
                    {formik.errors.inverter_type}
                  </Typography>
                )}
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Power Rating (W)"
                name="power_rating"
                type="number"
                value={formik.values.power_rating}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.power_rating && Boolean(formik.errors.power_rating)}
                helperText={formik.touched.power_rating && formik.errors.power_rating}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Frequency (Hz)"
                name="frequency"
                type="number"
                value={formik.values.frequency}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.frequency && Boolean(formik.errors.frequency)}
                helperText={formik.touched.frequency && formik.errors.frequency}
                fullWidth
                required
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                label="Efficiency (%)"
                name="efficiency"
                type="number"
                value={formik.values.efficiency}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.efficiency && Boolean(formik.errors.efficiency)}
                helperText={formik.touched.efficiency && formik.errors.efficiency}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Surge Power (W)"
                name="surge_power"
                type="number"
                value={formik.values.surge_power}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.surge_power && Boolean(formik.errors.surge_power)}
                helperText={formik.touched.surge_power && formik.errors.surge_power}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Warranty Years"
                name="warranty_years"
                type="number"
                value={formik.values.warranty_years}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.warranty_years && Boolean(formik.errors.warranty_years)}
                helperText={formik.touched.warranty_years && formik.errors.warranty_years}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Input Voltage (V)"
                name="input_voltage"
                type="number"
                value={formik.values.input_voltage}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.input_voltage && Boolean(formik.errors.input_voltage)}
                helperText={formik.touched.input_voltage && formik.errors.input_voltage}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Output Voltage (V)"
                name="output_voltage"
                type="number"
                value={formik.values.output_voltage}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.output_voltage && Boolean(formik.errors.output_voltage)}
                helperText={formik.touched.output_voltage && formik.errors.output_voltage}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12} align="center">
              <Button type="button" variant="contained" color="primary" sx={{ mt: 2 }} onClick={handleDialogOpen}>
                Submit
              </Button>
            </Grid>
          </Grid>
        </form>

        <Dialog
          open={open}
          onClose={handleDialogClose}
          aria-labelledby="alert-dialog-title"
          aria-describedby="alert-dialog-description"
        >
          <DialogTitle id="alert-dialog-title">{"Confirm Submission"}</DialogTitle>
          <DialogContent>
            <DialogContentText id="alert-dialog-description">
              Are you sure you want to submit this form?
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleDialogClose} color="primary">
              Cancel
            </Button>
            <Button onClick={formik.handleSubmit} color="primary" autoFocus>
              Confirm
            </Button>
          </DialogActions>
        </Dialog>

        <Dialog
          open={alertDialogOpen}
          onClose={handleAlertDialogClose}
          aria-labelledby="alert-dialog-alert-title"
          aria-describedby="alert-dialog-alert-description"
        >
          <DialogTitle id="alert-dialog-alert-title">{alert?.severity === 'success' ? 'Success' : 'Error'}</DialogTitle>
          <DialogContent>
            <DialogContentText id="alert-dialog-alert-description">
              {alert?.message}
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleAlertDialogClose} color="primary" autoFocus>
              Close
            </Button>
          </DialogActions>
        </Dialog>
      </Paper>
    </Container>
  );
};

export default ProductForm;
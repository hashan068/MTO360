import React, { useState } from 'react';
import { Box, Typography, TextField, Button, Alert, Container, Paper, Grid, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import api from './../../api';

// Validation schema using Yup

const validationSchema = Yup.object({
  name: Yup.string().required('Name is required'),
  email: Yup.string().email('Invalid email address').required('Email is required'),
  phone: Yup.string().required('Phone number is required'),
  street_address: Yup.string().required('Street address is required'),
  city: Yup.string().required('City is required'),
});

const CustomerForm = () => {
  const navigate = useNavigate();
  const [alert, setAlert] = useState(null);
  const [open, setOpen] = useState(false);
  const [alertDialogOpen, setAlertDialogOpen] = useState(false);

  const formik = useFormik({
    initialValues: {
      name: '',
      email: '',
      phone: '',
      street_address: '',
      city: '',
    },
    validationSchema: validationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      setOpen(false);  // Close confirmation dialog
      try {
        const response = await api.post('/api/sales/customers/', values);

        if (response.status === 201) {
          setAlert({ severity: 'success', message: 'Customer created successfully.' });
          formik.resetForm();
          setAlertDialogOpen(true);
          setTimeout(() => {
            setAlertDialogOpen(false);
            navigate('/sales/customer');  // Redirect to product page after 3 seconds
          }, 3000);
        } else {
          setAlert({ severity: 'error', message: `Error creating customer: ${response.data.error || 'Unknown error'}` });
          setAlertDialogOpen(true);
        }
      } catch (error) {
        console.error('Error creating customer:', error);
        setAlert({ severity: 'error', message: 'An error occurred while creating the customer.' });
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
          Customer Form
        </Typography>
        <form onSubmit={formik.handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                label="Name"
                name="name"
                value={formik.values.name}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.name && Boolean(formik.errors.name)}
                helperText={formik.touched.name && formik.errors.name}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Email"
                name="email"
                value={formik.values.email}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.email && Boolean(formik.errors.email)}
                helperText={formik.touched.email && formik.errors.email}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Phone"
                name="phone"
                value={formik.values.phone}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.phone && Boolean(formik.errors.phone)}
                helperText={formik.touched.phone && formik.errors.phone}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Street Address"
                name="street_address"
                value={formik.values.street_address}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.street_address && Boolean(formik.errors.street_address)}
                helperText={formik.touched.street_address && formik.errors.street_address}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="City"
                name="city"
                value={formik.values.city}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                error={formik.touched.city && Boolean(formik.errors.city)}
                helperText={formik.touched.city && formik.errors.city}
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

export default CustomerForm;

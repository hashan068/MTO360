import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../../../api';
import { Formik } from 'formik';
import * as Yup from 'yup';
import {
  Box,
  Typography,
  Button,
  TextField,
  FormControl,
  FormControlLabel,
  Checkbox,
  Grid,
  ThemeProvider,
  createTheme,
  Stack,
} from '@mui/material';

const theme = createTheme({
  palette: {
    primary: {
      main: '#6200ea',
    },
    secondary: {
      main: '#03dac6',
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
  },
  components: {
    MuiTextField: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

const SupplierForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [initialValues, setInitialValues] = useState({
    name: '',
    email: '',
    address: '',
    website: '',
    isActive: true,
    notes: '',
  });

  const [submitAction, setSubmitAction] = useState('close');

  useEffect(() => {
    if (id) {
      api
        .get(`/api/inventory/suppliers/${id}/`)
        .then((response) => {
          const {
            name,
            email,
            address,
            website,
            is_active,
            notes,
          } = response.data;
          setInitialValues({
            name,
            email,
            address,
            website,
            isActive: is_active,
            notes,
          });
        })
        .catch((error) => console.error(error));
    }
  }, [id]);

  const validationSchema = Yup.object({
    name: Yup.string().required('Name is required'),
    email: Yup.string().email('Invalid email format').required('Email is required'),
    address: Yup.string().required('Address is required'),
    website: Yup.string().url('Invalid URL').nullable(),
    isActive: Yup.boolean(),
    notes: Yup.string().nullable(),
  });

  const handleSubmit = async (values, { setSubmitting, setFieldError, resetForm }) => {
    try {
      setSubmitting(true);

      const data = {
        name: values.name,
        email: values.email,
        address: values.address,
        website: values.website,
        is_active: values.isActive,
        notes: values.notes,
      };

      let response;
      if (id) {
        response = await api.put(`/api/inventory/suppliers/${id}/`, data);
      } else {
        response = await api.post('/api/inventory/suppliers/', data);
      }

      if (submitAction === 'close') {
        navigate(`/inventory/suppliers`);
      } else {
        resetForm();
        setInitialValues({
          name: '',
          email: '',
          address: '',
          website: '',
          isActive: true,
          notes: '',
        });
      }

      setSubmitting(false);
    } catch (error) {
      console.error(error);
      setFieldError('general', 'Failed to create supplier.');
      setSubmitting(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ p: 4, bgcolor: 'background.paper', boxShadow: 3, borderRadius: 2 }}>
        <Typography variant="h4" gutterBottom>
          {id ? 'Edit Supplier' : 'Create Supplier'}
        </Typography>
        <Formik
          initialValues={initialValues}
          validationSchema={validationSchema}
          enableReinitialize
          onSubmit={handleSubmit}
        >
          {({ values, errors, touched, handleChange, handleBlur, handleSubmit, isSubmitting }) => (
            <form onSubmit={handleSubmit}>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Name"
                    value={values.name}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    error={touched.name && Boolean(errors.name)}
                    helperText={touched.name && errors.name}
                    fullWidth
                    required
                    name="name"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Email"
                    value={values.email}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    error={touched.email && Boolean(errors.email)}
                    helperText={touched.email && errors.email}
                    fullWidth
                    required
                    name="email"
                    type="email"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Address"
                    value={values.address}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    error={touched.address && Boolean(errors.address)}
                    helperText={touched.address && errors.address}
                    fullWidth
                    required
                    name="address"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Website"
                    value={values.website}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    error={touched.website && Boolean(errors.website)}
                    helperText={touched.website && errors.website}
                    fullWidth
                    name="website"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={values.isActive}
                        onChange={handleChange}
                        name="isActive"
                        color="primary"
                      />
                    }
                    label="Active"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    label="Notes"
                    value={values.notes}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    error={touched.notes && Boolean(errors.notes)}
                    helperText={touched.notes && errors.notes}
                    fullWidth
                    name="notes"
                    multiline
                    rows={4}
                  />
                </Grid>
              </Grid>
              <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={() => navigate(-1)}
                  sx={{ flexGrow: 1 }}
                >
                  Back
                </Button>
                <Button
                  type="button"
                  variant="contained"
                  color="primary"
                  disabled={isSubmitting}
                  onClick={() => {
                    setSubmitAction('close');
                    handleSubmit();
                  }}
                  sx={{ flexGrow: 2 }}
                >
                  {id ? 'Update and Close' : 'Create and Close'}
                </Button>
                <Button
                  type="button"
                  variant="contained"
                  color="primary"
                  disabled={isSubmitting}
                  onClick={() => {
                    setSubmitAction('addNew');
                    handleSubmit();
                  }}
                  sx={{ flexGrow: 2 }}
                >
                  {id ? 'Update and Add New' : 'Create and Add New'}
                </Button>
              </Stack>
            </form>
          )}
        </Formik>
      </Box>
    </ThemeProvider>
  );
};

export default SupplierForm;

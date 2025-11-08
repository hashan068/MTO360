import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../../api';
import { Formik } from 'formik';
import * as Yup from 'yup';
import {
  Box,
  Typography,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  ThemeProvider,
  createTheme,
  Stack,
  Autocomplete,
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

const PRForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [initialValues, setInitialValues] = useState({
    component: null, // Change from componentId to component
    quantity: '',

    notes: '',
    priority: 'high',
  });

  const [components, setComponents] = useState([]);
  const [submitAction, setSubmitAction] = useState('close');

  useEffect(() => {
    const fetchComponents = async () => {
      try {
        const response = await api.get('/api/inventory/components/');
        setComponents(response.data);
      } catch (error) {
        console.error('Error fetching components:', error);
      }
    };

    fetchComponents();

    if (id) {
      api
        .get(`/api/inventory/purchase-requisitions/${id}/`)
        .then((response) => {
          const {
            component,
            quantity,
            notes,
            priority,
          } = response.data;
          setInitialValues({
            component,
            quantity,
            notes,
            priority,
          });
        })
        .catch((error) => console.error(error));
    }
  }, [id]);

  const validationSchema = Yup.object({
    component: Yup.object().required('Component is required'),
    quantity: Yup.number()
      .required('Quantity is required')
      .positive('Quantity must be a positive number'),

    notes: Yup.string(),
    priority: Yup.string().required('Priority is required'),
  });

  const handleSubmit = async (values, { setSubmitting, setFieldError, resetForm }) => {
    try {
      setSubmitting(true);

      const data = {
        component_id: values.component.id, // Use values.component.id instead of values.componentId
        quantity: parseInt(values.quantity, 10),

        notes: values.notes,
        priority: values.priority,
      };

      let response;
      if (id) {
        response = await api.put(`/api/inventory/purchase-requisitions/${id}/`, data);
      } else {
        response = await api.post('/api/inventory/purchase-requisitions/', data);
      }

      const { id: newId } = response.data;

      if (submitAction === 'close') {
        navigate(`/inventory/purchase-requisition/${newId}`);
      } else {
        resetForm();
        setInitialValues({
          component: null,
          quantity: 0,
          notes: '',
          priority: 'high',
        });
      }

      setSubmitting(false);
    } catch (error) {
      console.error(error);
      setFieldError('general', 'Failed to create purchase requisition.');
      setSubmitting(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ p: 4, bgcolor: 'background.paper', boxShadow: 3, borderRadius: 2 }}>
        <Typography variant="h4" gutterBottom>
          {id ? 'Edit Purchase Requisition' : 'Create Purchase Requisition'}
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
                <Grid item xs={12}>
                  <Autocomplete
                    options={components}
                    value={values.component}
                    onChange={(event, newValue) => {
                      handleChange({
                        target: { name: 'component', value: newValue },
                      });
                    }}
                    getOptionLabel={(option) => option.name || ''}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="Component"
                        error={touched.component && Boolean(errors.component)}
                        helperText={touched.component && errors.component}
                        required
                      />
                    )}
                    isOptionEqualToValue={(option, value) => option.id === value.id}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    label="Quantity"
                    value={values.quantity}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    error={touched.quantity && Boolean(errors.quantity)}
                    helperText={touched.quantity && errors.quantity}
                    type="number"
                    fullWidth
                    required
                    name="quantity"
                  />
                </Grid>
                <Grid item xs={12}>

                </Grid>
                <Grid>
                  <InputLabel>Priority</InputLabel>
                  <Select
                    value={values.priority}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    error={touched.priority && Boolean(errors.priority)}
                    name="priority"
                  >
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="low">Low</MenuItem>
                  </Select>
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
                    multiline
                    rows={4}
                    name="notes"
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

export default PRForm;
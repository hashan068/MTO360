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

const ComponentForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [initialValues, setInitialValues] = useState({
    name: '',
    description: '',
    quantity: 0,
    reorderLevel: 0,
    unitOfMeasure: '',
    cost: 0,
  });

  const [submitAction, setSubmitAction] = useState('close');

  useEffect(() => {
    if (id) {
      api
        .get(`/api/inventory/components/${id}/`)
        .then((response) => {
          const {
            name,
            description,
            quantity,
            reorder_level,
            unit_of_measure,
            cost,
          } = response.data;
          setInitialValues({
            name,
            description,
            quantity,
            reorderLevel: reorder_level,
            unitOfMeasure: unit_of_measure,
            cost,
          });
        })
        .catch((error) => console.error(error));
    }
  }, [id]);

  const validationSchema = Yup.object({
    name: Yup.string().required('Name is required'),
    description: Yup.string().required('Description is required'),
    quantity: Yup.number()
      .required('Quantity is required')
      .positive('Quantity must be a positive number'),
    reorderLevel: Yup.number()
      .required('Reorder Level is required')
      .positive('Reorder Level must be a positive number'),
    unitOfMeasure: Yup.string().required('Unit of Measure is required'),
    cost: Yup.number()
      .required('Cost is required')
      .positive('Cost must be a positive number'),
  });

  const handleSubmit = async (values, { setSubmitting, setFieldError, resetForm }) => {
    try {
      setSubmitting(true);

      const data = {
        name: values.name,
        description: values.description,
        quantity: parseInt(values.quantity, 10),
        reorder_level: parseInt(values.reorderLevel, 10),
        unit_of_measure: values.unitOfMeasure,
        cost: parseFloat(values.cost),
      };

      let response;
      if (id) {
        response = await api.put(`/api/inventory/components/${id}/`, data);
      } else {
        response = await api.post('/api/inventory/components/', data);
      }

      const { id: newId } = response.data;

      if (submitAction === 'close') {
        navigate(`/inventory/component`);
      } else {
        resetForm();
        setInitialValues({
          name: '',
          description: '',
          quantity: 0,
          reorderLevel: 0,
          unitOfMeasure: '',
          cost: 0,
        });
      }

      setSubmitting(false);
    } catch (error) {
      console.error(error);
      setFieldError('general', 'Failed to create component.');
      setSubmitting(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ p: 4, bgcolor: 'background.paper', boxShadow: 3, borderRadius: 2 }}>
        <Typography variant="h4" gutterBottom>
          {id ? 'Edit Component' : 'Create Component'}
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
                    label="Description"
                    value={values.description}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    error={touched.description && Boolean(errors.description)}
                    helperText={touched.description && errors.description}
                    fullWidth
                    required
                    name="description"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
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
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Reorder Level"
                    value={values.reorderLevel}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    error={touched.reorderLevel && Boolean(errors.reorderLevel)}
                    helperText={touched.reorderLevel && errors.reorderLevel}
                    type="number"
                    fullWidth
                    required
                    name="reorderLevel"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth required>
                    <InputLabel>Unit of Measure</InputLabel>
                    <Select
                      value={values.unitOfMeasure}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={touched.unitOfMeasure && Boolean(errors.unitOfMeasure)}
                      name="unitOfMeasure"
                    >
                      <MenuItem value="pcs">Pieces</MenuItem>
                      <MenuItem value="kg">Kilograms</MenuItem>
                      <MenuItem value="l">Liters</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    label="Cost"
                    value={values.cost}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    error={touched.cost && Boolean(errors.cost)}
                    helperText={touched.cost && errors.cost}
                    type="number"
                    fullWidth
                    required
                    name="cost"
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
}

export default ComponentForm;

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
  TextField,
  Grid,
  Container,
  Alert,
} from '@mui/material';
import { IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { Autocomplete } from '@mui/material';
import { styled } from '@mui/system';
import { useFormik, FormikProvider, Form, FieldArray } from 'formik';
import * as Yup from 'yup';
import api from './../../api';

const StyledContainer = styled(Container)(({ theme }) => ({
  padding: theme.spacing(4),
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
  boxShadow: theme.shadows[2],
}));

const StyledTableContainer = styled(TableContainer)(({ theme }) => ({
  marginTop: theme.spacing(3),
}));

const StyledButton = styled(Button)(({ theme }) => ({
  marginTop: theme.spacing(3),
  alignSelf: 'center',
  padding: theme.spacing(1.5, 4),
}));

const QuotationForm = () => {
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [alert, setAlert] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const customersResponse = await api.get('/api/sales/customers/');
        setCustomers(customersResponse.data);

        const productsResponse = await api.get('/api/sales/products/');
        setProducts(productsResponse.data.map(product => ({
          id: product.id,
          name: product.product_name,
          description: product.description,
          price: parseFloat(product.price),
          bom: product.bom
        })));

        if (formik.values.customer) {
          formik.setFieldValue('invoicingAndShippingAddress', getCustomerAddress(formik.values.customer.id));
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setAlert({ severity: 'error', message: 'Error fetching data: ' + error.message });
      }
    };

    fetchData();
  }, []); // Dependency array is correct for running only once

  const getCustomerAddress = (customerId) => {
    const customer = customers.find((customer) => customer.id === customerId);
    if (customer) {
      return `${customer.street_address}, ${customer.city}`;
    } else {
      return '';
    }
  };

  const addItemValidationSchema = Yup.object({
    newProduct: Yup.object().nullable().required('Please select a product.'),
    newQuantity: Yup.number()
      .min(1, 'Quantity must be greater than 0')
      .required('Please enter a quantity.'),
  });

  const validationSchema = Yup.object({
    customer: Yup.object().nullable().required('Please select a customer.'),
    date: Yup.string().required('Please enter a date.'),
    expirationDate: Yup.string()
      .required('Please enter an expiration date.')
      .test('is-greater', 'Expiration date must be later than the date', function (value) {
        const { date } = this.parent;
        return date && value && new Date(value) > new Date(date);
      }),
    invoicingAndShippingAddress: Yup.string().required('Please enter an invoicing and shipping address.'),
    quotationItems: Yup.array()
      .of(
        Yup.object().shape({
          product: Yup.object().nullable().required('Please select a product.'),
          quantity: Yup.number().min(1, 'Quantity must be at least 1').required('Please enter a quantity.'),
        }),
      )
      .min(1, 'Please add at least one item to the quotation.'),
  });

  const formik = useFormik({
    initialValues: {
      customer: null,
      date: '',
      expirationDate: '',
      invoicingAndShippingAddress: '',
      quotationItems: [],
      newProduct: null,
      newQuantity: '',
    },
    validationSchema,
    onSubmit: async (values) => {
      const userId = localStorage.getItem('user_id');
      const quotationData = {
        date: values.date,
        expiration_date: values.expirationDate,
        invoicing_and_shipping_address: values.invoicingAndShippingAddress,
        customer: values.customer.id,
        quotation_items: values.quotationItems.map((item) => ({
          product: item.product.id,
          quantity: item.quantity,
          unit_price: item.product.price,
        })),
        created_by: userId,
      };

      try {
        const response = await api.post('/api/sales/quotations/', quotationData);

        if (response.status === 201) {
          setAlert({ severity: 'success', message: 'Quotation Created Successfully!' });
          formik.resetForm();
          setTimeout(() => setAlert(null), 3000);
        } else {
          setAlert({ severity: 'error', message: `Error creating quotation: ${response.data.error || 'Unknown error'}` });
        }
      } catch (error) {
        console.error('Error creating quotation:', error);
        setAlert({ severity: 'error', message: 'An error occurred while creating the quotation. Please try again later.' });
      }
    },
  });
  return (
    <StyledContainer maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Quotation Form
      </Typography>
      <div>
        {alert && <Alert severity={alert.severity}>{alert.message}</Alert>}
      </div>
      <FormikProvider value={formik}>
        <Form>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Autocomplete
                options={customers}
                getOptionLabel={(option) => option.name}
                value={formik.values.customer}
                onChange={(event, newValue) => {
                  formik.setFieldValue('customer', newValue);
                  formik.setFieldValue('invoicingAndShippingAddress', newValue ? getCustomerAddress(newValue.id) : '');
                }}
                renderInput={(params) => <TextField {...params} label="Customer" />}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                type="date"
                label="Date"
                InputLabelProps={{ shrink: true }}
                value={formik.values.date}
                onChange={formik.handleChange('date')}
                error={Boolean(formik.touched.date && formik.errors.date)}
                helperText={formik.touched.date && formik.errors.date}
                fullWidth
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                type="date"
                label="Expiration Date"
                InputLabelProps={{ shrink: true }}
                value={formik.values.expirationDate}
                onChange={formik.handleChange('expirationDate')}
                error={Boolean(formik.touched.expirationDate && formik.errors.expirationDate)}
                helperText={formik.touched.expirationDate && formik.errors.expirationDate}
                fullWidth
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Invoicing Address"
                value={formik.values.invoicingAndShippingAddress}
                onChange={formik.handleChange('invoicingAndShippingAddress')}
                error={Boolean(formik.touched.invoicingAndShippingAddress && formik.errors.invoicingAndShippingAddress)}
                helperText={formik.touched.invoicingAndShippingAddress && formik.errors.invoicingAndShippingAddress}
                fullWidth
                multiline
                rows={4}
              />
            </Grid>
          </Grid>

          <StyledTableContainer component={Paper}>
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
                <FieldArray name="quotationItems">
                  {({ push, remove }) => (
                    <>
                      {formik.values.quotationItems.map((item, index) => (
                        <TableRow key={index}>
                          <TableCell>{item.product?.name}</TableCell>
                          <TableCell align="right">{item.quantity}</TableCell>
                          <TableCell align="right">{item.product?.price}</TableCell>
                          <TableCell align="right">{item.quantity * item.product?.price}</TableCell>
                          <TableCell align="right">
                            <IconButton
                              aria-label="delete"
                              color="error"
                              onClick={() => remove(index)}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                      <TableRow>
                        <TableCell>
                          <Grid container spacing={2} alignItems="center">
                            <Grid item xs={8}>
                              <Autocomplete
                                options={products}
                                value={formik.values.newProduct}
                                onChange={(event, newValue) => formik.setFieldValue('newProduct', newValue)}
                                getOptionLabel={(option) => option.name}
                                renderOption={(props, option) => (
                                  <li {...props} key={option.id}>
                                    {option.name}
                                  </li>
                                )}
                                renderInput={(params) => <TextField {...params} label="Product" margin="normal" />}
                                sx={{ width: '100%' }}
                              />
                            </Grid>
                            <Grid item xs={4}>
                              <TextField
                                type="number"
                                value={formik.values.newQuantity}
                                onChange={formik.handleChange('newQuantity')}
                                label="Quantity"
                                fullWidth
                                error={Boolean(formik.touched.newQuantity && formik.errors.newQuantity)}
                                helperText={formik.touched.newQuantity && formik.errors.newQuantity}
                                InputProps={{
                                  inputProps: {
                                    min: 1,
                                  },
                                }}
                              />
                            </Grid>
                          </Grid>
                        </TableCell>
                        <TableCell align="right">
                          <Button
                            variant="contained"
                            onClick={() => {
                              if (formik.values.newProduct) {
                                addItemValidationSchema.validate({
                                  newProduct: formik.values.newProduct,
                                  newQuantity: formik.values.newQuantity,
                                }).then(() => {
                                  formik.setFieldValue('quotationItems', [
                                    ...formik.values.quotationItems,
                                    {
                                      product: formik.values.newProduct,
                                      quantity: formik.values.newQuantity,
                                    },
                                  ]);
                                  formik.setFieldValue('newProduct', null);
                                  formik.setFieldValue('newQuantity', '');
                                  formik.setFieldTouched('newProduct', false);
                                  formik.setFieldTouched('newQuantity', false);
                                }).catch((error) => {
                                  console.log(error.errors);
                                });
                              } else {
                                formik.setFieldTouched('newProduct', true, true);
                              }
                            }}
                            fullWidth
                          >
                            Add Item
                          </Button>
                        </TableCell>
                      </TableRow>

                    </>
                  )}
                </FieldArray>
              </TableBody>
            </Table>
          </StyledTableContainer>

          <StyledButton type="submit" variant="contained" color="primary">
            Submit Quotation
          </StyledButton>
        </Form>
      </FormikProvider>
    </StyledContainer >
  );
};

export default QuotationForm;
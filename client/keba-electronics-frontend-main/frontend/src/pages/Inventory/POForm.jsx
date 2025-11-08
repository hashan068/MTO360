import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../../api';
import { Formik, Form, Field } from 'formik';
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
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import { Assignment, Edit, CheckCircle, Cancel, ArrowBack, PriorityHigh, Receipt, LocalShipping } from '@mui/icons-material';

const theme = createTheme({
  palette: {
    primary: { main: '#6200ea' },
    secondary: { main: '#03dac6' },
    warning: { main: '#ffa000' },
    error: { main: '#d32f2f' },
    success: { main: '#43a047' },
  },
  typography: { h4: { fontWeight: 600 } },
  components: {
    MuiTextField: { styleOverrides: { root: { borderRadius: 8 } } },
    MuiButton: { styleOverrides: { root: { borderRadius: 8 } } },
  },
});

const STATUS_CHOICES = [
  { value: 'draft', label: 'Draft', icon: <Edit /> },
  { value: 'open_order', label: 'Open Order', icon: <Assignment /> },
  { value: 'approved', label: 'Approved', icon: <CheckCircle /> },
  { value: 'received', label: 'Received', icon: <LocalShipping /> },
  { value: 'invoiced', label: 'Invoiced', icon: <Receipt /> },
  { value: 'cancelled', label: 'Cancelled', icon: <Cancel /> },
  { value: 'rejected', label: 'Rejected', icon: <Cancel /> },
];

const POForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [purchaseOrder, setPurchaseOrder] = useState(null);
  const [suppliers, setSuppliers] = useState([]);
  const [requisitions, setRequisitions] = useState([]);
  const [initialValues, setInitialValues] = useState({
    purchaseRequisitionId: '',
    supplierId: '',
    status: 'draft',
    notes: '',
    price_per_unit: '',
    total_price: '',
  });
  const [confirmDialog, setConfirmDialog] = useState({ open: false, title: '', content: '', onConfirm: null });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [suppliersRes, requisitionsRes] = await Promise.all([
          api.get('/api/inventory/suppliers/'),
          api.get('/api/inventory/purchase-requisitions/?status=created'),
        ]);
        setSuppliers(suppliersRes.data);
        setRequisitions(requisitionsRes.data);

        if (id) {
          const orderRes = await api.get(`/api/inventory/purchase-orders/${id}/`);
          setPurchaseOrder(orderRes.data);
          setInitialValues({
            purchaseRequisitionId: orderRes.data.purchase_requisition_id,
            supplierId: orderRes.data.supplier_id,
            status: orderRes.data.status,
            notes: orderRes.data.notes,
            price_per_unit: orderRes.data.price_per_unit,
            total_price: orderRes.data.total_price,
          });
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    fetchData();
  }, [id]);

  const validationSchema = Yup.object({
    purchaseRequisitionId: Yup.number().required('Purchase Requisition is required'),
    supplierId: Yup.number().required('Supplier is required'),
    status: Yup.string().required('Status is required'),
    notes: Yup.string(),
    price_per_unit: Yup.number().required('Price Per Unit is required').min(0, 'Price Per Unit must be a positive number'),
  });

  const handleSubmit = async (values, { setSubmitting, resetForm }) => {
    try {
      const data = {
        purchase_requisition_id: values.purchaseRequisitionId,
        supplier_id: values.supplierId,
        status: values.status,
        notes: values.notes,
        price_per_unit: values.price_per_unit,
      };

      if (id) {
        if (purchaseOrder.status !== 'draft') {
          setConfirmDialog({
            open: true,
            title: 'Cannot Edit Order',
            content: `This order is in '${purchaseOrder.status}' status and cannot be edited.`,
            onConfirm: () => setConfirmDialog({ open: false }),
          });
          return;
        }
        await api.patch(`/api/inventory/purchase-orders/${id}/`, data);
      } else {
        await api.post('/api/inventory/purchase-orders/', data);
        resetForm();
      }
      navigate('/inventory/purchase-orders');
    } catch (error) {
      console.error('Error submitting purchase order:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (id && purchaseOrder && purchaseOrder.status !== 'draft') {
    return (
      <ThemeProvider theme={theme}>
        <Box sx={{ p: 4, bgcolor: 'background.paper', boxShadow: 3, borderRadius: 2 }}>
          <Typography variant="h4" gutterBottom>Cannot Edit Purchase Order</Typography>
          <Typography variant="body1" gutterBottom>
            This purchase order is in '{purchaseOrder.status}' status and cannot be edited.
          </Typography>
          <Button variant="contained" color="primary" onClick={() => navigate(-1)} startIcon={<ArrowBack />}>
            Go Back
          </Button>
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ p: 4, bgcolor: 'background.paper', boxShadow: 3, borderRadius: 2 }}>
        <Typography variant="h4" gutterBottom>
          {id ? 'Edit Purchase Order' : 'Create Purchase Order'}
        </Typography>
        <Formik
          initialValues={initialValues}
          validationSchema={validationSchema}
          enableReinitialize
          onSubmit={handleSubmit}
        >
          {({ values, errors, touched, handleChange, handleBlur, isSubmitting, setFieldValue }) => (
            <Form>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Field
                    name="purchaseRequisitionId"
                    render={({ field }) => (
                      <Autocomplete
                        {...field}
                        options={requisitions}
                        getOptionLabel={(option) => `${option.id} - ${option.component_id} (Qty: ${option.quantity})`}
                        onChange={(_, value) => setFieldValue(field.name, value ? value.id : '')}
                        renderInput={(params) => (
                          <TextField
                            {...params}
                            label="Purchase Requisition"
                            variant="outlined"
                            error={touched.purchaseRequisitionId && Boolean(errors.purchaseRequisitionId)}
                            helperText={touched.purchaseRequisitionId && errors.purchaseRequisitionId}
                            required
                          />
                        )}
                        renderOption={(props, option) => (
                          <Box component="li" {...props}>
                            <Grid container alignItems="center">
                              <Grid item xs={6}><Typography>{option.id} - {option.component_id}</Typography></Grid>
                              <Grid item xs={3}><Typography>Qty: {option.quantity}</Typography></Grid>
                              <Grid item xs={3}>
                                <Chip icon={<PriorityHigh />} label={option.priority} color={option.priority === 'high' ? 'error' : 'primary'} size="small" />
                              </Grid>
                            </Grid>
                          </Box>
                        )}
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Field
                    name="supplierId"
                    render={({ field }) => (
                      <Autocomplete
                        {...field}
                        options={suppliers}
                        getOptionLabel={(option) => `${option.id} - ${option.name}`}
                        onChange={(_, value) => setFieldValue(field.name, value ? value.id : '')}
                        renderInput={(params) => (
                          <TextField
                            {...params}
                            label="Supplier"
                            variant="outlined"
                            error={touched.supplierId && Boolean(errors.supplierId)}
                            helperText={touched.supplierId && errors.supplierId}
                            required
                          />
                        )}
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControl fullWidth required>
                    <InputLabel>Status</InputLabel>
                    <Select
                      name="status"
                      value={values.status}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      error={touched.status && Boolean(errors.status)}
                    >
                      {STATUS_CHOICES.map((choice) => (
                        <MenuItem key={choice.value} value={choice.value}>
                          {choice.icon} {choice.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    label="Notes"
                    name="notes"
                    value={values.notes}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    error={touched.notes && Boolean(errors.notes)}
                    helperText={touched.notes && errors.notes}
                    fullWidth
                    multiline
                    rows={4}
                    placeholder="Any additional information or comments..."
                  />
                </Grid>
                <Grid item xs={12}>
                  <Field
                    name="price_per_unit"
                    render={({ field, form }) => (
                      <TextField
                        {...field}
                        label="Price Per Unit"
                        variant="outlined"
                        type="number"
                        InputProps={{ inputProps: { min: 0 } }}
                        error={form.touched.price_per_unit && Boolean(form.errors.price_per_unit)}
                        helperText={form.touched.price_per_unit && form.errors.price_per_unit}
                        required
                      />
                    )}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Field
                    name="total_price"
                    render={({ field }) => (
                      <TextField
                        {...field}
                        label="Total Price"
                        variant="outlined"
                        disabled
                      />
                    )}
                  />
                </Grid>
              </Grid>
              <Stack direction="row" spacing={2} sx={{ mt: 3 }}>
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={() => navigate(-1)}
                  startIcon={<ArrowBack />}
                >
                  Back
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  disabled={isSubmitting}
                  startIcon={id ? <Edit /> : <Assignment />}
                  sx={{ flexGrow: 1 }}
                >
                  {id ? 'Update Order' : 'Create Order'}
                </Button>
              </Stack>
            </Form>
          )}
        </Formik>
      </Box>
      <Dialog open={confirmDialog.open} onClose={() => setConfirmDialog({ open: false })}>
        <DialogTitle>{confirmDialog.title}</DialogTitle>
        <DialogContent>
          <DialogContentText>{confirmDialog.content}</DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialog({ open: false })} color="primary">OK</Button>
        </DialogActions>
      </Dialog>
    </ThemeProvider>
  );
};

export default POForm;

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography, Container, Grid, Card, CardHeader, CardContent, Button,
  AppBar, Toolbar, Box, Stepper, Step, StepLabel, Skeleton, Chip, Alert, TableContainer,
  Table, TableHead, TableRow, TableCell, TableBody, Paper
} from '@mui/material';
import {
  Assignment, Edit, CheckCircle, Cancel, ArrowBack, PriorityHigh, LocalShipping, Receipt
} from '@mui/icons-material';
import api from '../../../api';

const STATUS_CHOICES = [
  { value: 'draft', label: 'Draft', icon: <Edit /> },
  { value: 'open_order', label: 'Open Order', icon: <Assignment /> },
  { value: 'approved', label: 'Approved', icon: <CheckCircle /> },
  { value: 'received', label: 'Received', icon: <LocalShipping /> },
  { value: 'invoiced', label: 'Invoiced', icon: <Receipt /> },
];

const getStatusStep = (status) => {
  const index = STATUS_CHOICES.findIndex((choice) => choice.value === status);
  return index === -1 ? 0 : index;
};

const getStatusChip = (status) => {
  const choice = STATUS_CHOICES.find((c) => c.value === status) || STATUS_CHOICES[STATUS_CHOICES.length - 1];
  return (
    <Chip
      icon={choice.icon}
      label={choice.label}
      color={status === 'approved' || status === 'received' || status === 'invoiced' ? 'success' : status === 'rejected' || status === 'cancelled' ? 'error' : 'primary'}
      variant={status === 'draft' || status === 'open_order' ? 'outlined' : 'filled'}
    />
  );
};

// Utils
export function ccyFormat(num) {
  return `${num.toFixed(2)}`;
}

export function priceRow(qty, unit) {
  return qty * unit;
}

export function createRow(desc, qty, unit) {
  const price = priceRow(qty, unit);
  return { desc, qty, unit, price };
}

// InvoiceTable component
const InvoiceTable = ({ rows }) => {
  const invoiceSubtotal = rows.map(({ price }) => price).reduce((sum, i) => sum + i, 0);
  return (
    <TableContainer component={Paper}>
      <Table sx={{ minWidth: 800 }} aria-label="spanning table">
        <TableHead>
       
          <TableRow>
            <TableCell width="600px">Desc</TableCell>
            <TableCell width="300px" align="right">Qty.</TableCell>
            <TableCell width="300px" align="right">Price per Unit</TableCell>
            <TableCell width="300px" align="right">Sum</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.desc}>
              <TableCell>{row.desc}</TableCell>
              <TableCell align="right">{row.qty}</TableCell>
              <TableCell align="right">{ccyFormat(row.unit)}</TableCell>
              <TableCell align="right">{ccyFormat(row.price)}</TableCell>
            </TableRow>
          ))}
          <TableRow sx={{ minWidth: 800 }} >
            <TableCell colSpan={4}>Total</TableCell>
            <TableCell  align="right">{ccyFormat(invoiceSubtotal)}</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </TableContainer>
  );
};

const POView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [purchaseOrder, setPurchaseOrder] = useState({
    price_per_unit: '',
    total_price: '',
    purchase_requisition: { quantity: 1 }
  });
  const [rows, setRows] = useState([createRow('Paperclips (Box)', 100, 1.15)]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPurchaseOrder = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await api.get(`/api/inventory/purchase-orders/${id}/`);
        setPurchaseOrder(response.data);
        setRows([createRow('Paperclips (Box)', response.data.purchase_requisition.quantity, parseFloat(response.data.price_per_unit))]);
      } catch (error) {
        console.error('Error fetching purchase order:', error);
        setError(error.message || 'An error occurred while fetching the purchase order.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchPurchaseOrder();
  }, [id]);

  return (
    <Container maxWidth="lg" sx={{ py: 4, px: 2, bgcolor: '#f5f5f5' }}>
      <AppBar position="static" color="default" sx={{ mb: 4 }}>
        <Toolbar>
          <Button startIcon={<ArrowBack />} onClick={() => navigate(-1)}>Back</Button>
          <Typography variant="h6" sx={{ flexGrow: 1, ml: 2 }}>
            Purchase Order #{isLoading ? 'Loading...' : purchaseOrder?.id || 'N/A'}
          </Typography>
        </Toolbar>
      </AppBar>
  
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
  
      {isLoading ? (
        <Grid container spacing={2}>
          <Grid item xs={12}><Skeleton variant="rectangular" height={60} /></Grid>
          <Grid item xs={12}><Skeleton variant="rectangular" height={300} /></Grid>
        </Grid>
      ) : purchaseOrder ? (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Box sx={{ width: '100%', mb: 4 }}>
              <Stepper activeStep={getStatusStep(purchaseOrder.status)} alternativeLabel>
                {STATUS_CHOICES.slice(0, -1).map((choice) => (
                  <Step key={choice.value}>
                    <StepLabel>{choice.label}</StepLabel>
                  </Step>
                ))}
              </Stepper>
            </Box>
          </Grid>
  
          <Grid item xs={12} md={12}>
            <Card sx={{ boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
              <CardHeader
                title="Purchase Order Details"
                action={getStatusChip(purchaseOrder.status)}
              />
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Box sx={{ p: 2, bgcolor: '#f0f0f0', borderRadius: 1 }}>
                      <Grid container spacing={2}>
                        <Grid item xs={6}><Typography><strong>Purchase Requisition ID:</strong> {purchaseOrder.purchase_requisition?.id || 'N/A'}</Typography></Grid>
                        <Grid item xs={6}><Typography><strong>Component ID:</strong> {purchaseOrder.purchase_requisition?.component_id || 'N/A'}</Typography></Grid>
                        <Grid item xs={6}><Typography><strong>Quantity:</strong> {purchaseOrder.purchase_requisition?.quantity || 'N/A'}</Typography></Grid>
                        <Grid item xs={6}>
                          <Typography><strong>Priority:</strong> </Typography>
                          <Chip
                            icon={<PriorityHigh />}
                            label={purchaseOrder.purchase_requisition?.priority || 'N/A'}
                            color={purchaseOrder.purchase_requisition?.priority === 'high' ? 'error' : 'primary'}
                            size="small"
                          />
                        </Grid>
                        
                        <Grid item xs={6}><Typography><strong>Created By:</strong> User {purchaseOrder.creator_id || 'N/A'}</Typography></Grid>
                        <Grid item xs={6}><Typography><strong>Updated At:</strong> {purchaseOrder.updated_at ? new Date(purchaseOrder.updated_at).toLocaleString() : 'N/A'}</Typography></Grid>
                      </Grid>
                    </Box>
                  </Grid>
                  <Grid item xs={6}><Typography><strong>Supplier ID:</strong> {purchaseOrder.supplier_id || 'N/A'}</Typography></Grid>
                  <InvoiceTable
                    rows={rows}
                  />
  
                  <Grid item xs={12}>
                    <Typography><strong>Notes:</strong> </Typography>
                    <Box sx={{ p: 1, bgcolor: '#f0f0f0', borderRadius: 1 }}>{purchaseOrder.notes || 'N/A'}</Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      ) : (
        <Typography>No purchase order found or an error occurred.</Typography>
      )}
    </Container>
  );
};

export default POView;

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Typography, Container, Grid, Card, CardHeader, CardContent, Button, AppBar, Toolbar, Box, Stepper, Step, StepLabel, Skeleton } from '@mui/material';
import api from '../../api';

const MfgOrderDetails = () => {
  const { id } = useParams();
  const [manufacturingOrder, setManufacturingOrder] = useState(null);
  const [bomId, setBomId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isMaterialRequested, setIsMaterialRequested] = useState(false);
  const [status, setStatus] = useState('pending');

  useEffect(() => {
    const fetchManufacturingOrder = async () => {
      setIsLoading(true);
      try {
        const response = await api.get(`/api/manufacturing/manufacturing-orders/${id}/`);
        setManufacturingOrder(response.data);
        fetchBomId(response.data.product_id);
        setStatus(response.data.status);
      } catch (error) {
        console.error('Error fetching manufacturing order:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchManufacturingOrder();
  }, [id]);

  const fetchBomId = async (productId) => {
    try {
      const response = await api.get(`/api/sales/products/${productId}/`);
      setBomId(response.data.bom);
      console.log(response.data.bom);
    } catch (error) {
      console.error('Error fetching BOM ID:', error);
    }
  };

  const handleMaterialRequest = async () => {
    try {
      const payload = {
        manufacturing_order: id,
        bom: bomId
      };
      await api.post(`/api/manufacturing/material-requisitions/`, payload);
      setIsMaterialRequested(true);
      setStatus('mr_sent');
      const response = await api.get(`/api/manufacturing/manufacturing-orders/${id}/`);
      setManufacturingOrder(response.data);
    } catch (error) {
      console.error('Error requesting material:', error);
    }
  };

  const handleStatusUpdate = async (newStatus) => {
    try {
      await api.patch(`/api/manufacturing/manufacturing-orders/${id}/`, { status: newStatus });
      setStatus(newStatus);
      const response = await api.get(`/api/manufacturing/manufacturing-orders/${id}/`);
      setManufacturingOrder(response.data);
      // Also update the corresponding sales order status if starting production
      if (newStatus === 'in_production') {
        await api.patch(`/api/sales/orders/${manufacturingOrder.sales_order_item}/`, { status: 'in_production' });
      }
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const renderStatusControls = () => {
    switch (status) {
      case 'pending':
        return (
          <Button
            variant="contained"
            color="success"
            onClick={handleMaterialRequest}
            disabled={isMaterialRequested}
          >
            {isMaterialRequested ? 'Material Requisition Sent' : 'Material Request'}
          </Button>
        );
      case 'mr_sent':
        return <Typography variant="body1">Material requisition sent</Typography>;
      case 'mr_approved':
        return (
          <Button
            variant="contained"
            color="primary"
            onClick={() => handleStatusUpdate('in_production')}
          >
            Start Production
          </Button>
        );
      case 'in_production':
        return (
          <Button
            variant="contained"
            color="primary"
            onClick={() => handleStatusUpdate('completed')}
          >
            Mark as Completed
          </Button>
        );
      case 'mr_rejected':
        return (
          <Box display="flex" alignItems="center">
            <Typography variant="body1" sx={{ mr: 1 }}>
              Rejected
            </Typography>
            <RejectedLogo />
          </Box>
        );
      case 'completed':
        return <Typography variant="body1">Completed</Typography>;
      case 'cancelled':
        return <Typography variant="body1">Cancelled</Typography>;
      default:
        return null;
    }
  };

  const STATUS_CHOICES = [
    { value: 'pending', label: 'Pending' },
    { value: 'mr_sent', label: 'MR Sent' },
    { value: 'mr_approved', label: 'MR Approved' },
    // { value: 'mr_rejected', label: 'MR Rejected' },
    { value: 'in_production', label: 'In Production' },
    { value: 'completed', label: 'Completed' },
    // { value: 'cancelled', label: 'Cancelled' },
  ];

  const getStatusStep = (status) => {
    return STATUS_CHOICES.findIndex(choice => choice.value === status);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4, px: 2, bgcolor: '#f5f5f5' }}>
      <AppBar position="static" color="default" sx={{ mb: 4 }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Manufacturing Order Details
          </Typography>
          {/* <Button variant="contained" color="primary" sx={{ mx: 1 }}>
            Edit
          </Button>
          <Button variant="contained" color="secondary" sx={{ mx: 1 }}>
            Delete
          </Button> */}
          {renderStatusControls()}
        </Toolbar>
      </AppBar>
      {isLoading ? (
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Skeleton variant="rectangular" height={60} />
          </Grid>
          <Grid item xs={12}>
            <Skeleton variant="rectangular" height={300} />
          </Grid>
        </Grid>
      ) : (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Box sx={{ width: '100%', mb: 4 }}>
              <Stepper activeStep={getStatusStep(manufacturingOrder?.status)} alternativeLabel>
                {STATUS_CHOICES.map((choice) => (
                  <Step key={choice.value}>
                    <StepLabel>{choice.label}</StepLabel>
                  </Step>
                ))}
              </Stepper>
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Card sx={{ boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
              <CardHeader title="Order Details" />
              <CardContent>
                <Grid container spacing={2}>
                  {[
                    { label: 'Order ID:', value: manufacturingOrder?.id || 'N/A' },
                    { label: 'Sales Order ID:', value: manufacturingOrder?.sales_order || 'N/A' },
                    { label: 'Product ID:', value: manufacturingOrder?.product_id || 'N/A' },
                    { label: 'Quantity:', value: manufacturingOrder?.quantity || 'N/A' },
                    { label: 'BOM ID:', value: bomId || 'N/A' },
                    { label: 'Status:', value: manufacturingOrder?.status || 'N/A' },
                    { label: 'Created At:', value: manufacturingOrder?.created_at ? new Date(manufacturingOrder.created_at).toLocaleString() : 'N/A' },
                    { label: 'Updated At:', value: manufacturingOrder?.updated_at ? new Date(manufacturingOrder.updated_at).toLocaleString() : 'N/A' },
                    { label: 'Sales Order Item:', value: manufacturingOrder?.sales_order_item || 'N/A' },
                  ].map((item, index) => (
                    <Grid item xs={12} sm={6} key={index}>
                      <div style={{ display: 'flex', alignItems: 'center' }}>
                        <Typography variant="body1" gutterBottom sx={{ color: '#666', fontWeight: 'bold', marginRight: '0.5rem' }}>
                          {item.label}
                        </Typography>
                        <Typography variant="body1" gutterBottom sx={{ color: '#666' }}>
                          {item.value}
                        </Typography>
                      </div>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};


const RejectedLogo = () => {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
};

export default MfgOrderDetails;
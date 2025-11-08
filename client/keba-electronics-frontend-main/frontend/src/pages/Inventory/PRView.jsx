import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Typography, Container, Grid, Card, CardHeader, CardContent, Button, AppBar, Toolbar, Box, Stepper, Step, StepLabel, Skeleton } from '@mui/material';
import api from '../../api';

const PRView = () => {
  const { id } = useParams();
  const [purchaseRequisition, setPurchaseRequisition] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState('created');

  useEffect(() => {
    const fetchPurchaseRequisition = async () => {
      setIsLoading(true);
      try {
        const response = await api.get(`/api/inventory/purchase-requisitions/${id}/`);
        setPurchaseRequisition(response.data);
        setStatus(response.data.status);
      } catch (error) {
        console.error('Error fetching purchase requisition:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchPurchaseRequisition();
  }, [id]);

  const handleStatusUpdate = async (newStatus) => {
    try {
      await api.patch(`/api/inventory/purchase-requisitions/${id}/`, { status: newStatus });
      setStatus(newStatus);
      const response = await api.get(`/api/inventory/purchase-requisitions/${id}/`);
      setPurchaseRequisition(response.data);

      // If the new status is "fulfilled", create a replenish transaction
      if (newStatus === 'fulfilled') {
        await createReplenishTransaction(purchaseRequisition);
      }
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const createReplenishTransaction = async (purchaseRequisition) => {
    try {
      const userId = localStorage.getItem('user_id');
  
      const replenishTransactionData = {
        purchase_requisition: purchaseRequisition.id,
        component: purchaseRequisition.component_id,
        quantity: purchaseRequisition.quantity,
        user: userId, // Retrieve user ID from local storage
      };
  
      // Make the API call to create the replenish transaction
      const response = await api.post('/api/inventory/replenish-transactions/', replenishTransactionData);
      console.log('Replenish transaction created successfully:', response.data);
    } catch (error) {
      console.error('Error creating replenish transaction:', error);
    }
  };

  const renderStatusControls = () => {
    switch (status) {
      case 'created':
        return (
          <Button
            variant="contained"
            color="primary"
            onClick={() => handleStatusUpdate('pending')}
          >
            Submit for Approval
          </Button>
        );
      case 'pending':
        return (
          <>
            <Button
              variant="contained"
              color="primary"
              onClick={() => handleStatusUpdate('approved')}
            >
              Approve
            </Button>
            <Button
              variant="contained"
              color="secondary"
              onClick={() => handleStatusUpdate('rejected')}
            >
              Reject
            </Button>
          </>
        );
      case 'approved':
        return (
          <Button
            variant="contained"
            color="primary"
            onClick={() => handleStatusUpdate('fulfilled')}
          >
            Mark as Fulfilled
          </Button>
        );
      case 'rejected':
        return (
          <>
            <Button
              variant="contained"
              color="primary"
              onClick={() => handleStatusUpdate('created')}
            >
              Revise and Resubmit
            </Button>
            <RejectedLogo />
          </>
        );

      case 'fulfilled':
        return <Typography variant="body1">Fulfield</Typography>;
      default:
        return <Typography variant="body1">Unknown status</Typography>;
    }
  };

  const STATUS_CHOICES = [
    { value: 'created', label: 'Created' },
    { value: 'pending', label: 'Pending' },
    { value: 'approved', label: 'Approved' },
    { value: 'fulfilled', label: 'Fulfilled' },
  ];

  const getStatusStep = (status) => {
    return STATUS_CHOICES.findIndex(choice => choice.value === status);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 2, px: 2, bgcolor: '#f5f5f5' }}>
      <AppBar position="static" color="default" sx={{ mb: 3 }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Purchase Requisition Details
          </Typography>
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
            <Box sx={{ width: '100%', mb: 1 }}>
              <Stepper activeStep={getStatusStep(purchaseRequisition?.status)} alternativeLabel>
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
              <CardHeader title="Purchase Requisition Details" />
              <CardContent>
                <Grid container spacing={2}>
                  {[
                    { label: 'Requisition ID:', value: purchaseRequisition?.id || 'N/A' },
                    { label: 'Component ID:', value: purchaseRequisition?.component_id || 'N/A' },
                    { label: 'Quantity:', value: purchaseRequisition?.quantity || 'N/A' },
                    { label: 'Priority:', value: purchaseRequisition?.priority || 'N/A' },
                    { label: 'Status:', value: purchaseRequisition?.status || 'N/A' },
                    { label: 'Created At:', value: purchaseRequisition?.created_at ? new Date(purchaseRequisition.created_at).toLocaleString() : 'N/A' },
                    { label: 'Updated At:', value: purchaseRequisition?.updated_at ? new Date(purchaseRequisition.updated_at).toLocaleString() : 'N/A' },
                    { label: 'Notes:', value: purchaseRequisition?.notes || 'N/A' },
                    { label: 'Expected Delivery Date:', value: purchaseRequisition?.expected_delivery_date ? new Date(purchaseRequisition.expected_delivery_date).toLocaleString() : 'N/A' },
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

export default PRView;

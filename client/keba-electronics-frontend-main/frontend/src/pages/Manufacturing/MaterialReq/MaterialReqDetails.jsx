import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../../api';
import {
  Typography,
  Container,
  Grid,
  Card,
  CardHeader,
  CardContent,
  Button,
  AppBar,
  Toolbar,
  Box,
  LinearProgress,
  Snackbar,
  Alert,
  Table,
  TableHead,
  TableBody,
  TableCell,
  TableRow,
  TableContainer,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import { USER_ID } from '../../../constants';

const steps = [
  'Pending',
  'partialy_approved',
  'approved',
  'fulfilled',

];

const getStatusStep = (status) => {
  switch (status) {
    case 'pending':
      return 0;
    case 'partialy_approved':
      return 1;
    case 'approved':
      return 2;
    case 'fulfilled':
      return 4;
    default:
      return 0;
  }
};

const MaterialReqDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [materialReq, setMaterialReq] = useState(null);
  const [components, setComponents] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [alert, setAlert] = useState(null);
  const [role, setRole] = useState(null);

  useEffect(() => {
    const userRole = localStorage.getItem('userrole');
    setRole(userRole);
  }, []);

  useEffect(() => {
    const fetchMaterialReq = async () => {
      try {
        const response = await api.get(`/api/manufacturing/material-requisitions/${id}/`);
        setMaterialReq(response.data);
        await fetchComponents(response.data.items);
      } catch (error) {
        console.error('Error fetching material requisition:', error);
        setError('Error fetching material requisition');
      } finally {
        setIsLoading(false);
      }
    };

    const fetchComponents = async (items) => {
      const componentIds = items.map(item => item.component);
      const uniqueComponentIds = [...new Set(componentIds)];

      try {
        const responses = await Promise.all(uniqueComponentIds.map(id => api.get(`/api/inventory/components/${id}/`)));
        const componentsData = responses.reduce((acc, res) => {
          acc[res.data.id] = res.data.name;
          return acc;
        }, {});
        setComponents(componentsData);
      } catch (error) {
        console.error('Error fetching components:', error);
        setError('Error fetching components');
      }
    };

    fetchMaterialReq();
  }, [id]);

  const handleApproveRequisition = async () => {
    const approvedItems = [];
    const rejectedItems = [];

    // Approve each item in the material requisition
    for (const item of materialReq.items) {
      // Check if the item status is pending
      if (item.status === 'pending') {
        // Approve the item only if its status is pending
        const itemApproved = await handleApproveRequisitionItem(item);
        if (itemApproved) {
          approvedItems.push(item);
        } else {
          rejectedItems.push(item);
        }
      } else {
        // If the item status is not pending, skip approval
        console.log(`Skipping approval for item ${item.id} because its status is not pending.`);
      }
    }


    if (approvedItems.length > 0) {
      setAlert({ severity: 'success', message: 'Material requisition approved successfully' });
      setMaterialReq((prev) => ({ ...prev, status: 'approved' }));
    }

    if (rejectedItems.length > 0) {
      setAlert({ severity: 'error', message: 'Some items could not be approved due to insufficient component quantity' });
    }
  };

  const handleApproveRequisitionItem = async (item) => {
    const userId = parseInt(localStorage.getItem(USER_ID), 10);

    const payload = {
      material_requisition_item: item.id,
      component_id: item.component,
      quantity: item.quantity,
      user_id: userId,
      status: 'approved',
    };

    try {
      const response = await api.post('/api/inventory/consumption-transactions/', payload);

      if (response.status === 200 || response.status === 201) {
        console.log('Material requisition item approved:', item.id);
        const response = await api.get(`/api/manufacturing/material-requisitions/${id}/`);
        setMaterialReq(response.data);
        return true;
      } else if (response.status === 401) {
        // Handle unauthorized error
        console.error('Authentication credentials were not provided.');
        setAlert({ severity: 'error', message: 'Authentication credentials were not provided. Please log in and try again.' });
        return false;
      } else {
        console.error('Error approving material requisition item:', response.data);
        setAlert({ severity: 'error', message: 'An error occurred while approving the material requisition item. Please try again later.' });
        return false;
      }
    } catch (error) {
      console.error('Error approving material requisition item:', error);
      setAlert({ severity: 'error', message: 'An error occurred while approving the material requisition item. Please try again later.' });
      return false;
    }
  };


  const handleDismissAlert = () => {
    setAlert(null);
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, px: 2, bgcolor: '#f5f5f5' }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="h4" gutterBottom>
              Loading...
            </Typography>
          </Grid>
        </Grid>
      </Container>
    );
  }


  return (
    <Container maxWidth="lg" sx={{ py: 4, px: 2, bgcolor: '#f5f5f5' }}>
      <AppBar position="static" color="default" sx={{ mb: 4 }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Material Requisition Details
          </Typography>
          <Button variant="contained" onClick={() => navigate(-1)}>
            Back
          </Button>
          {(materialReq.status === 'pending' || materialReq.status === 'partialy_approved') &&
            role === 'Inventory Manager' && (
              <Button
                variant="contained"
                color="primary"
                onClick={handleApproveRequisition}
                sx={{ ml: 2 }}
              >
                Approve
              </Button>
            )}
        </Toolbar>
      </AppBar>

      <Card sx={{ mb: 4, boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
        <CardContent>
          <Stepper activeStep={getStatusStep(materialReq.status)} alternativeLabel>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </CardContent>
      </Card>

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Card sx={{ boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
            {/* <CardHeader title="Material Requisition Details" /> */}
            <CardContent>
              <Grid container spacing={2}>
                {[
                  { label: 'Order ID:', value: materialReq.id },
                  { label: 'BOM ID:', value: materialReq.bom },
                  { label: 'Created At:', value: new Date(materialReq.created_at).toLocaleString() },
                  { label: 'Updated At:', value: new Date(materialReq.updated_at).toLocaleString() },
                ].map((item, index) => (
                  <React.Fragment key={index}>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body1" gutterBottom sx={{ color: '#666', fontWeight: 'bold' }}>
                        {item.label}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body1" gutterBottom sx={{ color: '#666' }}>
                        {item.value}
                      </Typography>
                    </Grid>
                  </React.Fragment>
                ))}
                <Grid item xs={12}>
                  <LinearProgress
                    color={materialReq.status === 'approved' ? 'success' : 'warning'}
                    variant="determinate"
                    value={materialReq.status === 'approved' ? 100 : 50}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12}>
          <Card sx={{ boxShadow: '0 2px 10px rgba(0,0,0,0.1)' }}>
            <CardHeader title="Items" />
            <CardContent>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>
                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                          Item ID
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                          Component
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                          Quantity
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                          Status
                        </Typography>
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {materialReq.items.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>{item.id}</TableCell>
                        <TableCell>{components[item.component] || 'Loading...'}</TableCell>
                        <TableCell>{item.quantity}</TableCell>
                        <TableCell>
                          <Typography
                            color={
                              item.status === 'approved'
                                ? 'success.main'
                                : item.status === 'rejected'
                                  ? 'error.main'
                                  : 'warning.main'
                            }
                          >
                            {item.status}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      <Snackbar
        open={!!alert}
        autoHideDuration={6000}
        onClose={handleDismissAlert}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert onClose={handleDismissAlert} severity={alert?.severity}>
          {alert?.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default MaterialReqDetails;

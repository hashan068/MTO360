import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Container,
  Grid,
  Card,
  CardHeader,
  CardContent,
  Skeleton,
  AppBar,
  Toolbar,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import api from '../../api';

const SalesOrderDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [salesOrder, setSalesOrder] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [salesOrderItems, setSalesOrderItems] = useState([]);
  const [role, setRole] = useState(null);
  const [username, setUsername] = useState(null);
  const [userId, setUserId] = useState(null);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const userRole = localStorage.getItem('userrole');
    const userName = localStorage.getItem('username');
    const userId = localStorage.getItem('user_id');
    setRole(userRole);
    setUsername(userName);
    setUserId(userId);
  }, []);

  useEffect(() => {
    const fetchSalesOrder = async () => {
      if (id) {
        setIsLoading(true);
        try {
          const { data } = await api.get(`/api/sales/orders/${id}/`);
          setSalesOrder(data);
          setSalesOrderItems(data.order_items);
          setStatus(data.status); // Set the status of the sales order
        } catch (error) {
          console.error(error);
        } finally {
          setIsLoading(false);
        }
      }
    };
    fetchSalesOrder();
  }, [id]);

  const STATUS_CHOICES = [
    // { value: 'pending', label: 'Pending' },
    { value: 'confirmed', label: 'Confirmed' },
    { value: 'processing', label: 'Processing' },
    { value: 'in_Production', label: 'In Production' },
    { value: 'Ready_for_delivery', label: 'Ready for Delivery' },
    // { value: 'cancelled', label: 'Cancelled' },
    // { value: 'delivered', label: 'Delivered' },
  ];

  const createManufacturingOrder = async (salesOrderItemId) => {
    const salesOrderItem = salesOrderItems.find(item => item.sales_order_item_id === salesOrderItemId);

    if (!salesOrderItem) return;

    try {
      const { data: product } = await api.get(`/api/sales/products/${salesOrderItem.product}/`);
      const manufacturingOrderData = {
        sales_order_item: salesOrderItem.sales_order_item_id,
        quantity: salesOrderItem.quantity,
        product_id: salesOrderItem.product,
        bom: product.bom,
        creater: userId,
      };

      console.log(manufacturingOrderData);

      const response = await api.post('/api/manufacturing/manufacturing-orders/', manufacturingOrderData);
      console.log(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleEdit = () => {
    navigate(`/salesorder/${id}`);
  };

  const handleManufacture = () => {
    salesOrderItems.forEach((item) => {
      createManufacturingOrder(item.sales_order_item_id);
    });
    handleStatusUpdate('in_production');
  };

  const getStatusStep = (status) => {
    return STATUS_CHOICES.findIndex(choice => choice.value === status);
  };

  const handleStatusUpdate = async (newStatus) => {
    try {
      const payload = { status: newStatus }; 

      console.log('Payload:', payload);

      await api.patch(`/api/sales/orders/${id}/`, payload);

      // Fetch and update the sales order state
      const response = await api.get(`/api/sales/orders/${id}/`);
      setSalesOrder(response.data);
      setStatus(newStatus);

      console.log('Status updated successfully:', newStatus);
    } catch (error) {
      if (error.response) {

      } else {
        console.error('Error message:', error.message);
      }
    }
  };

  const renderStatusControls = () => {
    switch (status) {
      case 'confirmed':
        if (role === 'Production Manager') {
          return (
            <Button
              variant="contained"
              color="primary"
              onClick={() => {
                handleStatusUpdate('processing');
                handleManufacture();
              }}
            >
              Manufacture
            </Button>
          );
        }
        break;
      // case 'confirmed':
      //   return (
      //     <Button variant="contained" color="primary" onClick={() => handleStatusUpdate('processing')}>
      //       Start Processing
      //     </Button>
      //   );
      case 'processing':
        return (
          <Button variant="contained" color="primary" onClick={() => handleStatusUpdate('in_Production')}>
            Start Production
          </Button>
        );
      case 'in_Production':
        return (
          <Button variant="contained" color="primary" onClick={() => handleStatusUpdate('Ready_for_delivery')}>
            Ready for Delivery
          </Button>
        );
      case 'Ready_for_delivery':
        return (
          <Button variant="contained" color="primary" onClick={() => handleStatusUpdate('delivered')}>
            Mark as Delivered
          </Button>
        );
      // case 'delivered':
      //   return <Typography variant="body1">Order Delivered</Typography>;
      // case 'cancelled':
      //   return <Typography variant="body1">Order Cancelled</Typography>;
      default:
        return null;
    }
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Skeleton variant="rectangular" height={60} />
          </Grid>
          <Grid item xs={12}>
            <Skeleton variant="rectangular" height={300} />
          </Grid>
        </Grid>
      </Container>
    );
  }

  if (!salesOrder) {
    return <div>Sales order not found.</div>;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 2, py: 4, px: 2, backgroundColor: '#eceff1' }}>
      <AppBar position="static" color="default" sx={{ mb: 4 }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {`Sales Order Details - ID ${salesOrder.id}`}
          </Typography>
          {renderStatusControls()}
        </Toolbar>
      </AppBar>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Box sx={{ width: '100%', mb: 4 }}>
            <Stepper activeStep={getStatusStep(salesOrder.status)} alternativeLabel>
              {STATUS_CHOICES.map((choice) => (
                <Step key={choice.value}>
                  <StepLabel>{choice.label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          </Box>
        </Grid>
        <Grid item xs={12}>
          <Card sx={{ boxShadow: '0px 2px 10px rgba(0, 0, 0, 0.1)' }}>
            <CardContent>
              <Typography variant="body1" gutterBottom sx={{ color: '#424242', fontWeight: 'bold' }}>
                Order ID: {salesOrder.id}
              </Typography>
              <Typography variant="body1" gutterBottom sx={{ color: '#424242', fontWeight: 'bold' }}>
                Customer: {salesOrder.customer_name}
              </Typography>
              <Typography variant="body1" gutterBottom sx={{ color: '#424242', fontWeight: 'bold' }}>
                Order Date: {new Date(salesOrder.created_at).toLocaleString()}
              </Typography>
              <Typography variant="body1" gutterBottom sx={{ color: '#424242', fontWeight: 'bold' }}>
                Status: {salesOrder.status}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12}>
          <Card sx={{ boxShadow: '0px 2px 10px rgba(0, 0, 0, 0.1)' }}>
            <CardHeader title="Order Items" />
            <CardContent>
              <TableContainer component={Paper}>
                <Table sx={{ minWidth: 650 }} aria-label="simple table">
                  <TableHead>
                    <TableRow>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>ID</TableCell>
                      <TableCell align="center" sx={{ fontWeight: 'bold' }}>Product</TableCell>
                      <TableCell align="center" sx={{ fontWeight: 'bold' }}>Quantity</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>Unit Price</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>Total Price</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {salesOrderItems.map((item) => (
                      <TableRow key={item.sales_order_item_id}>
                        <TableCell align="right">{item.sales_order_item_id}</TableCell>
                        <TableCell align="center">{item.product_name}</TableCell>
                        <TableCell align="center">{item.quantity}</TableCell>
                        <TableCell align="right">{item.price}</TableCell>
                        <TableCell align="right">{item.quantity * item.price}.00</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <Typography variant="body1" gutterBottom sx={{ color: '#424242', fontWeight: 'bold',marginTop: '16px', textAlign: 'right',marginRight: '14px' }}>
                Total : {salesOrder.total_amount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default SalesOrderDetails;

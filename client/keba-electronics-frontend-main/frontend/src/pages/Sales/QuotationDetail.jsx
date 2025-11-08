import React, { useEffect, useState } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, Container, Grid, Card, CardHeader, CardContent, AppBar, Toolbar, Alert } from '@mui/material';
import { useParams } from 'react-router-dom';
import { CheckCircle, Cancel } from '@mui/icons-material';
import api from '../../api';
import saveAs from 'file-saver';


export default function QuotationDetail() {
  const { id } = useParams();
  const [quotation, setQuotation] = useState(null);
  const [salesOrderItems, setSalesOrderItems] = useState([]);
  const [alert, setAlert] = useState(null);

  useEffect(() => {
    api.get(`/api/sales/quotations/${id}/`)
      .then((res) => {
        setQuotation(res.data);
        setSalesOrderItems(res.data.quotation_items);
      })
      .catch((err) => {
        console.log(err);
        setAlert({ severity: 'error', message: 'Error fetching quotation details' });
      });
  }, [id]);

  const handlePreview = () => {
    console.log('Preview clicked');
  };

  const handleConfirm = () => {
    console.log('Confirm clicked');
  };

  const handleDownload = () => {
    api
      .get(`/api/sales/quotations/${id}/download/`, {
        responseType: 'blob',
      })
      .then((res) => {
        const pdfBlob = new Blob([res.data], { type: 'application/pdf' });
        saveAs(pdfBlob, `quotation_${id}.pdf`);
      })
      .catch((err) => {
        if (err.response && err.response.status === 404) {
          setAlert({ severity: 'error', message: 'Quotation download URL not found' });
        } else {
          console.log(err);
          setAlert({ severity: 'error', message: 'Error downloading quotation' });
        }
      });
  };

  const validateForm = () => {
    return true;
  };

  const handleReject = async () => {
    try {
      const response = await api.patch(`/api/sales/quotations/${id}/`, { status: 'rejected' });
      setQuotation(response.data);
      setAlert({ severity: 'success', message: 'Quotation rejected successfully!' });
    } catch (error) {
      console.error('Error rejecting quotation:', error);
      setAlert({ severity: 'error', message: 'An error occurred while rejecting the quotation. Please try again later.' });
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!validateForm()) {
      return;
    }

    const salesOrderData = {
      customer: quotation.customer,
      order_items: salesOrderItems.map((item) => ({
        product: item.product,
        quantity: item.quantity,
        price: item.unit_price,
      })),
    };

    console.log('Sending data:', salesOrderData);

    try {
      const response = await api.post('/api/sales/orders/', salesOrderData);
      console.log('Received data:', response.data);

      if (response.status === 201) {
        setAlert({ severity: 'success', message: 'Sales order created successfully!' });
        setTimeout(() => {
          setAlert(null);
        }, 3000);
        setSalesOrderItems([]);

        // Update the quotation status to 'accepted'
        const updatedQuotation = await api.patch(`/api/sales/quotations/${id}/`, { status: 'accepted' });
        setQuotation(updatedQuotation.data);

      } else {
        setAlert({ severity: 'error', message: `Error creating sales order: ${response.data.error || 'Unknown error'}` });
      }
    } catch (error) {
      console.error('Error creating sales order:', error);
      setAlert({ severity: 'error', message: 'An error occurred while creating the sales order. Please try again later.' });
    }
  };

  const handleSendEmail = async () => {
    try {
      const response = await api.post(`/api/sales/quotations/${id}/send-email/`);

      if (response.status === 200) {
        setAlert({ severity: 'success', message: 'Email sent successfully!' });
      } else {
        setAlert({ severity: 'error', message: response.data.error || 'Error sending email' });
      }
    } catch (error) {
      console.error('Error sending email:', error);
      setAlert({ severity: 'error', message: 'An error occurred while sending the email. Please try again later.' });
    }
  };

  if (!quotation) {
    return <div>Loading...</div>;
  }

  return (
    <Box sx={{ flexGrow: 1, padding: 3 }}>
      <AppBar position="static" color="default" sx={{ mb: 4, mt: 2 }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Quotation Details - {quotation.id}
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', marginBottom: 3 }}>
            {quotation.status === 'pending' || quotation.status === 'quotation' && (
              <>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleSendEmail}
                  sx={{
                    backgroundColor: '#1a237e',
                    '&:hover': { backgroundColor: '#0d1b5e' },
                  }}
                >
                  Send Quotation Email
                </Button>
              </>
            )}
          </Box>

        </Toolbar>
      </AppBar>

      {alert && (
        <Alert severity={alert.severity} onClose={() => setAlert(null)} sx={{ marginBottom: 2 }}>
          {alert.message}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {[
              // { label: 'Quotation Number:', value: quotation.quotation_number },
              { label: 'Customer:', value: quotation.customer_name },
              { label: 'Date:', value: quotation.date },
              { label: 'Expiration Date:', value: quotation.expiration_date },
              { label: 'Invoicing and Shipping Address:', value: quotation.invoicing_and_shipping_address },
              // { label: 'Total Amount:', value: quotation.total_amount },
              { label: 'Status:', value: quotation.status },
            ].map(({ label, value }) => (
              <Box key={label} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="body1" component="dt" sx={{ flexBasis: '300px', fontWeight: 'bold' }}>{label}</Typography>
                <Typography component="dd" sx={{ flex: 1, textAlign: 'left', ml: 5 }}>{value}</Typography>
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>
      <Grid item xs={12}>
        <Card sx={{ boxShadow: '0px 2px 10px rgba(0, 0, 0, 0.1)' }}>
          <CardHeader title="Order Items" />
          <CardContent>
            <TableContainer component={Paper}>
              <Table sx={{ minWidth: 650 }} aria-label="simple table">
                <TableHead>
                  <TableRow>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>ID</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>Product</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>Quantity</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>Unit Price</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>Total Price</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {salesOrderItems.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell align="right">{item.id}</TableCell>
                      <TableCell align="right">{item.product}</TableCell>
                      <TableCell align="right">{item.quantity}</TableCell>
                      <TableCell align="right">{item.unit_price}</TableCell>
                      <TableCell align="right">{item.quantity * item.unit_price}.00</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <Typography variant="body1" gutterBottom sx={{ color: '#424242', fontWeight: 'bold', marginTop: '16px', textAlign: 'right', marginRight: '14px' }}>
              Total : {quotation.total_amount}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', marginBottom: 3 }}>
        {quotation.status === 'pending'  && (
          <>
            <Button
              variant="contained"
              color="success"
              startIcon={<CheckCircle />}
              sx={{ textTransform: 'none' }}
              onClick={handleSubmit}
            >
              Approve
            </Button>
            <Button
              variant="contained"
              color="error"
              startIcon={<Cancel />}
              sx={{ textTransform: 'none' }}
              onClick={handleReject}
            >
              Reject
            </Button>
          </>
        )}
      </Box>

      {/* <PreviewDownloadButtons 
        onPreview={handlePreview} 
        onDownload={handleDownload} 
      /> */}
    </Box>
  );
}

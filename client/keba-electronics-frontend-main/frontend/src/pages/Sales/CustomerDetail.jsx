import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Button,
  Paper,
  Container,
  CircularProgress,
  TextField,
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../api';
import pageAppbarStyles from '../../styles/pageAppbarStyles';

export default function CustomerDetail() {
  const { id } = useParams();
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const navigate = useNavigate();

  const getCustomer = () => {
    setLoading(true);
    api
      .get(`/api/sales/customers/${id}/`)
      .then((res) => {
        setCustomer(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    getCustomer();
  }, [id]);

  const handleEditClick = () => {
    setIsEditing(true);
  };

  const handleSaveClick = () => {
    api
      .put(`/api/sales/customers/${id}/`, customer, {
        headers: {
          'Content-Type': 'application/json',
        },
      })
      .then((res) => {
        setIsEditing(false);
        setCustomer(res.data); // Update customer state with latest data from server
      })
      .catch((err) => {
        if (err.response) {
          console.error('Error response:', err.response.data);
        } else {
          console.error('Error message:', err.message);
        }
      });
  };

  const handleChange = (e) => {
    setCustomer({
      ...customer,
      [e.target.name]: e.target.value,
    });
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="md" sx={pageAppbarStyles.container}>
      <Paper sx={pageAppbarStyles.paper}>
        <Typography variant="h6" sx={pageAppbarStyles.toolbar}>
          {isEditing ? 'Edit Customer' : 'Customer Details'}
        </Typography>
        {customer && (
          <Box component="form" noValidate autoComplete="off">
            <TextField
              label="Name"
              name="name"
              value={customer.name}
              onChange={handleChange}
              disabled={!isEditing}
              fullWidth
              margin="normal"
            />
            <TextField
              label="Email"
              name="email"
              value={customer.email}
              onChange={handleChange}
              disabled={!isEditing}
              fullWidth
              margin="normal"
            />
            <TextField
              label="Phone"
              name="phone"
              value={customer.phone}
              onChange={handleChange}
              disabled={!isEditing}
              fullWidth
              margin="normal"
            />
            <TextField
              label="Street Address"
              name="street_address"
              value={customer.street_address}
              onChange={handleChange}
              disabled={!isEditing}
              fullWidth
              margin="normal"
            />
            <TextField
              label="City"
              name="city"
              value={customer.city}
              onChange={handleChange}
              disabled={!isEditing}
              fullWidth
              margin="normal"
            />
            <Box sx={{ mt: 2 }}>
              {isEditing ? (
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleSaveClick}
                >
                  Save
                </Button>
              ) : (
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleEditClick}
                >
                  Edit
                </Button>
              )}
              <Button
                variant="outlined"
                color="secondary"
                onClick={() => navigate('/sales/customer')}
                sx={{ ml: 2 }}
              >
                Back
              </Button>
            </Box>
          </Box>
        )}
      </Paper>
    </Container>
  );
}

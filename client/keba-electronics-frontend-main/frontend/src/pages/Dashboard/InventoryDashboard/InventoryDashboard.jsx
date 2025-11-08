import React, { useState, useEffect } from 'react';
import {
  Typography,
  Grid,
  Container,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import api from '../../../api';
import InventoryStatistics from './InventoryStatistics';
import RecentTransactions from './RecentTransactions';
import InventoryLevels from './InventoryLevels';

export default function InventoryDashboard() {
  const navigate = useNavigate();
  const [purchaseRequisitions, setPurchaseRequisitions] = useState([]);
  const [components, setComponents] = useState([]);
  const [suppliers, setSuppliers] = useState([]);

  useEffect(() => {
    api.get('/api/inventory/purchase-requisitions/').then((res) => {
      setPurchaseRequisitions(res.data.slice(0, 5));
    });

    api.get('/api/inventory/components/').then((res) => {
      setComponents(res.data.slice(0, 5));
    });

    api.get('/api/inventory/suppliers/').then((res) => {
      setSuppliers(res.data.slice(0, 5));
    });
  }, []);



  const handleSeeAllComponents = () => {
    navigate('/inventory/component');
  };

  const handleSeeAllSuppliers = () => {
    navigate('/inventory/suppliers');
  };

  return (
    <Box sx={{ backgroundColor: '#f5f5f5', py: 4 }}>
      <Container maxWidth="lg">
        <Typography variant="h4" align="center" gutterBottom>
          Inventory Dashboard
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12}>
            <InventoryStatistics />
          </Grid>
          <Grid item xs={12}>
            <InventoryLevels />
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>

              <CardContent>
                <RecentTransactions />

              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={8}>
            <Card sx={{ height: '100%' }}>
              <CardHeader title="Inventory Details" />
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TableContainer component={Paper}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Name</TableCell>
                            <TableCell>Quantity</TableCell>
                            <TableCell>Reorder Level</TableCell>
                            <TableCell>Unit</TableCell>
                            <TableCell>Cost</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {components.map((component) => (
                            <TableRow key={component.id}>
                              <TableCell>{component.name}</TableCell>
                              <TableCell>{component.quantity}</TableCell>
                              <TableCell>{component.reorder_level}</TableCell>
                              <TableCell>{component.unit_of_measure}</TableCell>
                              <TableCell>{component.cost}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                    <Button variant="outlined" color="primary" onClick={handleSeeAllComponents}>
                      See All Components
                    </Button>
                  </Grid>
                  <Grid item xs={12}>
                    <TableContainer component={Paper}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Name</TableCell>
                            <TableCell>Email</TableCell>
                            <TableCell>Address</TableCell>
                            <TableCell>Website</TableCell>
                            <TableCell>Active</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {suppliers.map((supplier) => (
                            <TableRow key={supplier.id}>
                              <TableCell>{supplier.name}</TableCell>
                              <TableCell>{supplier.email}</TableCell>
                              <TableCell>{supplier.address}</TableCell>
                              <TableCell>{supplier.website}</TableCell>
                              <TableCell>{supplier.is_active.toString()}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                    <Button variant="outlined" color="primary" onClick={handleSeeAllSuppliers}>
                      See All Suppliers
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}
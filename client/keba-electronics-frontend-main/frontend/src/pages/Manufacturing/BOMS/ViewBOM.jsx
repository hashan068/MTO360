import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
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
} from '@mui/material';
import api from '../../../api';

const BOMView = () => {
  const { id } = useParams();
  const [bom, setBom] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [bomItems, setBomItems] = useState([]);

  useEffect(() => {
    const fetchBOM = async () => {
      if (id) {
        setIsLoading(true);
        try {
          const { data } = await api.get(`/api/manufacturing/bills-of-material/${id}/`);
          setBom(data);
          setBomItems(data.bom_items);
          console.log(data);
        } catch (error) {
          console.error(error);
        } finally {
          setIsLoading(false);
        }
      }
    };
    fetchBOM();
  }, [id]);

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

  if (!bom) {
    return <div>BOM not found.</div>;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 2, py: 4, px: 2, backgroundColor: '#b0bec5' }}>
      <Grid container spacing={3}>

        <Grid item xs={12}>
          <Card sx={{ boxShadow: '0px 2px 10px rgba(0, 0, 0, 0.1)' }}>
            <CardHeader
              title="BOM Details"

            />
            <CardContent>
              <Typography variant="body1" gutterBottom sx={{ color: '#666', fontWeight: 'bold' }}>
                BOM ID: {bom.id}
              </Typography>
              <Typography variant="body1" gutterBottom sx={{ color: '#666', fontWeight: 'bold' }}>
                Name: {bom.name}
              </Typography>
              <Typography variant="body1" gutterBottom sx={{ color: '#666', fontWeight: 'bold' }}>
                Product: {bom.product_name}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12}>
          <Card sx={{ boxShadow: '0px 2px 10px rgba(0, 0, 0, 0.1)' }}>
            <CardHeader title="BOM Items" />
            <CardContent>
              <TableContainer component={Paper}>
                <Table sx={{ minWidth: 650 }} aria-label="simple table">
                  <TableHead>
                    <TableRow>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>ID</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>Component</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>Quantity</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {bomItems.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell align="right">{item.id}</TableCell>
                        <TableCell align="right">{item.component_name}</TableCell>
                        <TableCell align="right">{item.quantity}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default BOMView;
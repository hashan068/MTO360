import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Button,
  Paper,
  Grid,
  Container,
  CircularProgress,
  TextField,
  Select,
  MenuItem,
  Toolbar,
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../../api';
import pageAppbarStyles from '../../styles/pageAppbarStyles';

export default function ProductDetails() {
  const { id } = useParams();
  const [product, setProduct] = useState({});
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    getProductDetails();
  }, []);

  const getProductDetails = () => {
    setLoading(true);
    api
      .get(`/api/sales/products/${id}/`)
      .then((res) => {
        setProduct(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const handleUpdateProduct = () => {
    setLoading(true);
    const updatedProduct = {
      ...product,
      name: `${product.inverter_type} ${product.power_rating}W ${product.frequency}Hz`,
      model_number: `INV-${product.inverter_type.substring(
        0,
        3
      ).toUpperCase()}-${product.power_rating}-${Math.round(product.frequency)}`,
    };
    api
      .patch(`/api/sales/products/${id}/`, updatedProduct)
      .then((res) => {
        setProduct(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setErrors(err.response.data);
        setLoading(false);
      });
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setProduct((prevProduct) => ({
      ...prevProduct,
      [name]: value,
    }));
  };

  const handleSelectChange = (event) => {
    const { name, value } = event.target;
    setProduct((prevProduct) => ({
      ...prevProduct,
      [name]: value,
    }));
  };

  return (
    <Container maxWidth="lg" sx={pageAppbarStyles.container}>
      <Paper sx={pageAppbarStyles.paper}>
        <Toolbar>
          <Typography variant="h6" sx={pageAppbarStyles.toolbar}>
            Product Details
          </Typography>
        </Toolbar>
      </Paper>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          {loading ? (
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                mt: 4,
              }}
            >
              <CircularProgress />
            </Box>
          ) : (
            <Paper sx={{ p: 2, height: 500 }}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    label="Product Name"
                    name="product_name"
                    value={`${product.inverter_type} ${product.power_rating}W ${product.frequency}Hz`}
                    InputProps={{
                      readOnly: true,
                    }}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    label="Description"
                    name="description"
                    value={product.description}
                    onChange={handleInputChange}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    label="Price"
                    name="price"
                    value={product.price}
                    onChange={handleInputChange}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <Select
                    label="Inverter Type"
                    name="inverter_type"
                    value={product.inverter_type}
                    onChange={handleSelectChange}
                    fullWidth
                  >
                    <MenuItem value="Square Wave">Square Wave</MenuItem>
                    <MenuItem value="Sine Wave">Sine Wave</MenuItem>
                  </Select>
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    label="Power Rating"
                    name="power_rating"
                    value={product.power_rating}
                    onChange={handleInputChange}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    label="Frequency"
                    name="frequency"
                    value={product.frequency}
                    onChange={handleInputChange}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    label="Efficiency"
                    name="efficiency"
                    value={product.efficiency}
                    onChange={handleInputChange}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    label="Surge Power"
                    name="surge_power"
                    value={product.surge_power}
                    onChange={handleInputChange}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    label="Warranty Years"
                    name="warranty_years"
                    value={product.warranty_years}
                    onChange={handleInputChange}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    label="Input Voltage"
                    name="input_voltage"
                    value={product.input_voltage}
                    onChange={handleInputChange}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    label="Output Voltage"
                    name="output_voltage"
                    value={product.output_voltage}
                    onChange={handleInputChange}
                    fullWidth
                  />
                </Grid>
              </Grid>
              <Button
                variant="contained"
                color="primary"
                sx={{ mt: 2, mb: 2, float: 'center'}}
                onClick={handleUpdateProduct}
              >
                Update Product
              </Button>
              {errors && (
                <Typography color="error">
                  {Object.keys(errors).map((key) => (
                    <div key={key}>{errors[key]}</div>
                  ))}
                </Typography>
              )}
            </Paper>
          )}
        </Grid>
      </Grid>
    </Container>
  );
}

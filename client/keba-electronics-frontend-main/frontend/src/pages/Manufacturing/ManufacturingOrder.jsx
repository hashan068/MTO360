import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Button,
  Paper,
  Grid,
  Container,
  CircularProgress,
  Toolbar,
  TextField,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  useTheme,
  useMediaQuery,
  Pagination
} from '@mui/material';
import {
  DataGrid,
  GridToolbarContainer,
  GridToolbarColumnsButton,
  GridToolbarFilterButton,
  GridToolbarExport,
  GridToolbarDensitySelector,
} from '@mui/x-data-grid';
import { useNavigate } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import pageAppbarStyles from '../../styles/pageAppbarStyles';
import api from '../../api';

const STATUS_CHOICES = {
  pending: { label: 'Pending', color: 'warning' },
  mr_sent: { label: 'MR Sent', color: 'primary' },
  mr_approved: { label: 'MR Approved', color: 'success' },
  mr_rejected: { label: 'MR Rejected', color: 'error' },
  in_production: { label: 'In Production', color: 'info' },
  completed: { label: 'Completed', color: 'success' },
  cancelled: { label: 'Cancelled', color: 'error' },
};

const renderStatusChip = (params) => {
  const status = params.value;
  const statusConfig = STATUS_CHOICES[status] || {};
  return (
    <Chip
      label={statusConfig.label}
      color={statusConfig.color}
      variant="outlined"
      size="small"
    />
  );
};

function CustomToolbar() {
  return (
    <GridToolbarContainer>
      <GridToolbarColumnsButton />
      <GridToolbarFilterButton />
      <GridToolbarDensitySelector
        slotProps={{ tooltip: { title: 'Change density' } }}
      />
      <Box sx={{ flexGrow: 1 }} />
      <GridToolbarExport
        slotProps={{
          tooltip: { title: 'Export data' },
          button: { variant: 'outlined' },
        }}
      />
    </GridToolbarContainer>
  );
}

export default function ManufacturingOrder() {
  const [manufacturingOrders, setManufacturingOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pageSize, setPageSize] = useState(8);
  const [page, setPage] = useState(1);
  const [searchText, setSearchText] = useState('');
  const [filteredManufacturingOrders, setFilteredManufacturingOrders] = useState([]);
  const navigate = useNavigate();

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const getManufacturingOrders = () => {
    setLoading(true);
    api.get('/api/manufacturing/manufacturing-orders/')
      .then((res) => {
        setManufacturingOrders(res.data);
        setFilteredManufacturingOrders(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    getManufacturingOrders();
  }, []);

  const handleRowClick = (params) => {
    navigate(`/mfg/mfgorder/${params.row.id}`);
  };

  // const handleAddManufacturingOrder = () => {
  //   navigate('/mfg/manufacturingorder/new');
  // };

  const handleSearchChange = (event) => {
    const value = event.target.value;
    setSearchText(value);
    const filteredData = manufacturingOrders.filter((order) =>
      Object.values(order).some((field) =>
        field.toString().toLowerCase().includes(value.toLowerCase())
      )
    );
    setFilteredManufacturingOrders(filteredData);
    setPage(1); // Reset to the first page whenever the search text changes
  };

  const handlePageChange = (event, newPage) => {
    setPage(newPage);
  };

  const columns = [
    { field: 'id', headerName: 'Order ID', width: 100 },
    { field: 'product_id', headerName: 'Product', width: 100 },
    
    { field: 'product_name', headerName: 'Product Name', width: 360 },
    {
      field: 'status',
      headerName: 'Status',
      width: 150,
      align : 'center', headerAlign: 'center',
      renderCell: renderStatusChip
    },
    {
      field: 'created_at_date',
      headerName: 'Manufacturing Order Date',
      type: 'date',
      width: 200,
      align : 'center', headerAlign: 'center',
      valueFormatter: (params) => params.value && new Date(params.value).toLocaleDateString(),
    },
    { field: 'quantity', headerName: 'Quantity', type: 'number', width: 150 },
    

  ];



  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Paper sx={pageAppbarStyles.paper}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Manufacturing Orders
          </Typography>
          <TextField
            variant="outlined"
            size="small"
            placeholder="Search..."
            value={searchText}
            onChange={handleSearchChange}
            InputProps={{
              startAdornment: <SearchIcon position="start" />,
            }}
            sx={{ marginRight: 2 }}
          />
          {/* <Button
            variant="contained"
            color="primary"
            onClick={handleAddManufacturingOrder}
            startIcon={<AddIcon />}
            sx={{
              backgroundColor: theme.palette.secondary.main,
              '&:hover': {
                backgroundColor: theme.palette.secondary.dark,
              },
            }}
          >
            Add Manufacturing Order
          </Button> */}
        </Toolbar>
      </Paper>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              <Paper sx={{ p: 2, height: 500 }}>
                <DataGrid
                  rows={filteredManufacturingOrders.slice((page - 1) * pageSize, page * pageSize)}
                  columns={columns}
                  pageSize={pageSize}
                  rowCount={filteredManufacturingOrders.length}
                  paginationMode="server"
                  onRowClick={handleRowClick}
                  slots={{
                    toolbar: CustomToolbar,
                  }}
                  sx={pageAppbarStyles.dataGrid}
                  hideFooter
                />
              </Paper>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                <FormControl variant="outlined" size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Rows per page</InputLabel>
                  <Select
                    value={pageSize}
                    onChange={(e) => setPageSize(e.target.value)}
                    label="Rows per page"
                  >
                    <MenuItem value={8}>8</MenuItem>
                    <MenuItem value={16}>16</MenuItem>
                    <MenuItem value={24}>24</MenuItem>
                  </Select>
                </FormControl>
                <Pagination
                  count={Math.ceil(filteredManufacturingOrders.length / pageSize)}
                  page={page}
                  onChange={handlePageChange}
                  color="primary"
                />
              </Box>
            </>
          )}
        </Grid>
      </Grid>
    </Container>
  );
}

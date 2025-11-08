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
  Stack,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Pagination,
} from '@mui/material';
import { DataGrid, GridToolbarContainer, GridToolbarColumnsButton, GridToolbarFilterButton, GridToolbarExport, GridToolbarDensitySelector } from '@mui/x-data-grid';
import { useNavigate } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import api from '../../api';
import { format } from 'date-fns';
import pageAppbarStyles from '../../styles/pageAppbarStyles';

const STATUS_CHOICES = {
  quotation: { label: 'Pending', color: 'default' },
  quotation_sent: { label: 'Quotation Sent', color: 'primary' },
  accepted: { label: 'Accepted', color: 'success' },
  rejected: { label: 'Rejected', color: 'error' },
  cancelled: { label: 'Cancelled', color: 'warning' },
  expired: { label: 'Expired', color: 'default' },
  pending: { label: 'Pending', color: 'warning' },
};

export default function Quotations() {
  const [quotations, setQuotations] = useState([]);
  const [filteredQuotations, setFilteredQuotations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [pageSize, setPageSize] = useState(8);
  const [page, setPage] = useState(1);

  const navigate = useNavigate();

  const getQuotations = () => {
    setLoading(true);
    api
      .get('/api/sales/quotations/')
      .then((res) => {
        setQuotations(res.data);
        setFilteredQuotations(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    getQuotations();
  }, []);

  const handleRowClick = (params) => {
    navigate(`/sales/quotation/${params.row.id}`);
  };

  const handleAddQuotation = () => {
    navigate('/sales/quotations/new');
  };

  const handleSearchChange = (event) => {
    const value = event.target.value;
    setSearchText(value);
    const filteredData = quotations.filter((quotation) =>
      Object.values(quotation).some((field) =>
        field.toString().toLowerCase().includes(value.toLowerCase())
      )
    );
    setFilteredQuotations(filteredData);
    setPage(1); // Reset to the first page whenever the search text changes
  };

  const handlePageChange = (event, newPage) => {
    setPage(newPage);
  };

  const handlePageSizeChange = (event) => {
    setPageSize(event.target.value);
    setPage(1); // Reset to the first page whenever the page size changes
  };

  function CustomToolbar() {
    return (
      <GridToolbarContainer sx={{ margin: '6px'}}>
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

  const columns = [
    { field: 'id', headerName: 'Quotation ID', width: 120 },
    { field: 'customer_name', headerName: 'Customer', width: 200 },
    {
      field: 'date',
      headerName: 'Quotation Date',
      type: 'date',
      width: 180,
      valueFormatter: (params) =>
        params.value && format(new Date(params.value), 'yyyy/MM/dd'),
    },
    {
      field: 'expiration_date',
      headerName: 'Expiration Date',
      type: 'date',
      width: 180,
      valueFormatter: (params) =>
        params.value && format(new Date(params.value), 'yyyy/MM/dd'),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 150,
      renderCell: renderStatusChip
    },
    { field: 'total_amount', headerName: 'Total Amount', type: 'number', width: 150 },
  ];

  return (
    <Container maxWidth="lg" sx={pageAppbarStyles.container}>
      <Paper sx={pageAppbarStyles.paper}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Quotations
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
          <Button
            variant="contained"
            color="primary"
            onClick={handleAddQuotation}
            startIcon={<AddIcon />}
          >
            Add Quotation
          </Button>
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
                  rows={filteredQuotations.slice((page - 1) * pageSize, page * pageSize)}
                  columns={columns}
                  pageSize={pageSize}
                  rowCount={filteredQuotations.length}
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
                    onChange={handlePageSizeChange}
                    label="Rows per page"
                  >
                    <MenuItem value={8}>8</MenuItem>
                    <MenuItem value={16}>16</MenuItem>
                    <MenuItem value={24}>24</MenuItem>
                  </Select>
                </FormControl>
                <Pagination
                  count={Math.ceil(filteredQuotations.length / pageSize)}
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

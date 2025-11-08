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
  Pagination,
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
import api from '../../../api';
import pageAppbarStyles from '../../../styles/pageAppbarStyles';

const STATUS_CHOICES = {
  pending: { label: 'Pending', color: 'warning' },
  approved: { label: 'Approved', color: 'success' },
  rejected: { label: 'Rejected', color: 'error' },
  partialy_approved: { label: 'Partially Approved', color: 'info' },
  fulfilled: { label: 'Fulfilled', color: 'success' },
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

const MaterialReq = () => {
  const [materialReqs, setMaterialReqs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [filteredMaterialReqs, setFilteredMaterialReqs] = useState([]);
  const [pageSize, setPageSize] = useState(8);
  const [page, setPage] = useState(1);

  const navigate = useNavigate();

  const fetchMaterialReqs = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/manufacturing/material-requisitions/');
      setMaterialReqs(response.data);
      setFilteredMaterialReqs(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching material requisitions:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMaterialReqs();
  }, []);

  const handleRowClick = (params) => {
    navigate(`/mfg/materialreq/${params.row.id}`);
  };

  const handleAddMaterialReq = () => {
    navigate('/mfg/materialreq/new');
  };

  const handleSearchChange = (event) => {
    const value = event.target.value;
    setSearchText(value);
    const filteredData = materialReqs.filter((materialReq) =>
      Object.values(materialReq).some((field) =>
        field.toString().toLowerCase().includes(value.toLowerCase())
      )
    );
    setFilteredMaterialReqs(filteredData);
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

  const columns = [
    { field: 'id', headerName: 'MR ID', width: 150, align : 'center', headerAlign: 'center' },
    {
      field: 'manufacturing_order',
      headerName: 'MO ID',
      width: 150, align : 'center', headerAlign: 'center'
      
    },

    {
      field: 'status',
      headerName: 'Status',
      width: 150,
      renderCell: renderStatusChip
    },
    {
      field: 'created_at_date',
      headerName: 'Created Date',
      width: 300,

    },
    {
      field: 'bom',
      headerName: 'BOM ID',
      width: 300,

    },

  ];

  return (
    <Container maxWidth="lg" sx={{ py: 3 }}>
      <Paper sx={pageAppbarStyles.paper}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Material Requisitions
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
            onClick={handleAddMaterialReq}
            startIcon={<AddIcon />}
          >
            Add Material Requisition
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
                  rows={filteredMaterialReqs.slice((page - 1) * pageSize, page * pageSize)}
                  columns={columns}
                  pageSize={pageSize}
                  rowCount={filteredMaterialReqs.length}
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
                  count={Math.ceil(filteredMaterialReqs.length / pageSize)}
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
};

export default MaterialReq;

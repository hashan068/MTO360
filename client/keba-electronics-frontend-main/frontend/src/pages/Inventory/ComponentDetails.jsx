import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import ComponentForm from './ComponentForm';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField } from '@mui/material';
import api from '../../api';

const ComponentDetails = () => {
  const { id } = useParams();
  const [openReplenishDialog, setOpenReplenishDialog] = useState(false);
  const [replenishQuantity, setReplenishQuantity] = useState(0);
  const [reorderLevel, setReorderLevel] = useState(0);
  const [unitOfMeasure, setUnitOfMeasure] = useState('');

  useEffect(() => {
    if (id) {
      api
        .get(`/api/inventory/components/${id}/`)
        .then((response) => {
          const { reorder_level, unit_of_measure } = response.data;
          setReorderLevel(reorder_level);
          setUnitOfMeasure(unit_of_measure);
        })
        .catch((error) => console.error(error));
    }
  }, [id]);

  const handleOpenReplenishDialog = () => {
    setOpenReplenishDialog(true);
  };

  const handleCloseReplenishDialog = () => {
    setOpenReplenishDialog(false);
    setReplenishQuantity(0);
  };

  const handleReplenish = async () => {
    try {
      const payload = {
        quantity: replenishQuantity,
      };
      await api.patch(`/api/inventory/components/${id}/`, payload);
      console.log('Component replenished successfully');
      handleCloseReplenishDialog();
    } catch (error) {
      console.error('Error replenishing component:', error);
    }
  };

  return (
    <div>
      <ComponentForm id={id} />
      <Button onClick={handleOpenReplenishDialog}>Replenish</Button>

      <Dialog open={openReplenishDialog} onClose={handleCloseReplenishDialog}>
        <DialogTitle>Replenish Component</DialogTitle>
        <DialogContent>
          <TextField
            label="Replenish Quantity"
            type="number"
            value={replenishQuantity}
            onChange={(e) => setReplenishQuantity(parseInt(e.target.value, 10))}
            fullWidth
          />
          <div>Reorder Level: {reorderLevel} {unitOfMeasure}</div>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseReplenishDialog}>Cancel</Button>
          {/* <Button onClick={handleReplenish} disabled={replenishQuantity <= 0}>
            Replenish
          </Button> */}
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default ComponentDetails;
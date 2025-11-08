import React, { useState } from 'react';
import { TextField, Button } from '@mui/material';
import api from '../../api';

const ReplenishInventory = ({ id }) => {
  const [quantity, setQuantity] = useState('');

  const handleReplenish = async () => {
    try {
      const payload = {
        component: id,
        quantity: Number(quantity) // Ensure quantity is a number
      };
      await api.post(`/api/replenish-transactions/`, payload);

    } catch (error) {
      console.error('Error replenishing inventory:', error);

    }
  };

  return (
    <div>
      <TextField
        label="Quantity"
        variant="outlined"
        type="number"
        value={quantity}
        onChange={(e) => setQuantity(e.target.value)}
      />
      <Button variant="contained" color="primary" onClick={handleReplenish}>
        Replenish Inventory
      </Button>
    </div>
  );
};

export default ReplenishInventory;

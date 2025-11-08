import React, { useState, useEffect } from'react';
import {
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Avatar,
  CircularProgress,
} from '@mui/material';
import RemoveCircleOutlineIcon from '@mui/icons-material/RemoveCircleOutline';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import api from '../../../api';

const RecentTransactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const [consumptionResponse, replenishResponse] = await Promise.all([
          api.get('/api/inventory/consumption-transactions/'),
          api.get('/api/inventory/replenish-transactions/'),
        ]);
        const combinedTransactions = [...consumptionResponse.data,...replenishResponse.data];
        combinedTransactions.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        setTransactions(combinedTransactions.slice(0, 5)); // show only the latest 5 transactions
        setLoading(false);
      } catch (error) {
        console.error('There was an error fetching the transactions!', error);
        setLoading(false);
      }
    };
    fetchTransactions();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', pt: 2 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ bgcolor: 'white', p: 2, borderRadius: '4px' }}>
      <Typography variant="h6" gutterBottom>
        Recent Transactions
      </Typography>
      <Stepper orientation="vertical" sx={{ py: 2 }}>
        {transactions.length > 0? (
          transactions.map(transaction => (
            <Step key={transaction.id}>
              <StepLabel
                icon={
                  transaction.type === 'consumption'? (
                    <Avatar sx={{ bgcolor:'red', width: 24, height: 24 }}>
                      <RemoveCircleOutlineIcon fontSize="small" />
                    </Avatar>
                  ) : (
                    <Avatar sx={{ bgcolor: 'green', width: 24, height: 24 }}>
                      <AddCircleOutlineIcon fontSize="small" />
                    </Avatar>
                  )
                }
              >
                {new Date(transaction.timestamp).toLocaleTimeString()}
              </StepLabel>
              <Box sx={{ p: 1, border: '1px solid #ccc', borderRadius: '4px', mb: 1 }}>
                <Typography variant="body1" sx={{ fontSize: 14 }}>
                  {`${transaction.component_name} X ${transaction.quantity} was ${transaction.type === 'consumption'?'Consumed' : 'Replanished'} by ${transaction.user_name} on ${new Date(transaction.timestamp).toLocaleString()}`}
                </Typography>
              </Box>
            </Step>
          ))
        ) : (
          <Typography sx={{ fontSize: 14, color: 'gray' }}>
            No transactions found.
          </Typography>
        )}
      </Stepper>
    </Box>
  );
};

export default RecentTransactions;
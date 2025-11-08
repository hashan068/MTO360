import React, { useState, useEffect } from 'react';
import { Paper, List, ListItem, ListItemText, CircularProgress, Typography } from '@mui/material';
import api from '../../../api';

const RecentActivity = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get('/api/manufacturing/manufacturing-orders/')
      .then(response => {
        const rawOrders = response.data;
        const oneWeekAgo = new Date();
        oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
        const recentOrders = rawOrders.filter(order => new Date(order.updated_at) >= oneWeekAgo);
        const formattedActivities = recentOrders.map(order => ({
          description: `Manufacturing Order ${order.id} status changed to ${order.status}`,
          timestamp: order.updated_at
        }));
        // Sort by timestamp in descending order and take the latest 6 activities
        const latestActivities = formattedActivities
          .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
          .slice(0, 6);
        setActivities(latestActivities);
        setLoading(false);
      })
      .catch(error => {
        setError('There was an error fetching the data!');
        console.error('There was an error fetching the data!', error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <Paper elevation={3} sx={{ padding: '20px' }}>
      <Typography variant="h6" gutterBottom>
        Recent Activity
      </Typography>
      <List>
        {activities.map((activity, index) => (
          <ListItem key={index}>
            <ListItemText
              primary={activity.description}
              secondary={new Date(activity.timestamp).toLocaleString()}
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default RecentActivity;

import React from 'react';
import notificationService from '../../services/notificationService';
import { Avatar, Typography, Box, Paper, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

const FloatingNotifications = ({ onClose }) => {
  const [notifications, setNotifications] = React.useState([]);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const data = await notificationService.getNotifications();
        setNotifications(data);
      } catch (err) {
        console.error("Failed to fetch notifications:", err);
        setError("Failed to load notifications. Please try again later.");
      }
    };

    fetchNotifications();
  }, []);

  return (
    <Paper
      elevation={3}
      sx={{
        position: 'fixed',
        top: 64,
        right: 20,
        backgroundColor: 'white',
        borderRadius: 4,
        padding: 2,
        maxWidth: 300,
        maxHeight: 400,
        overflowY: 'auto',
        zIndex: 1200,
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">Notifications</Typography>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </Box>
      {error && <p className="error">{error}</p>}
      {notifications.map((notification) => (
        <Box key={notification.id} sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar src={notification.avatar} sx={{ mr: 2 }} />
          <Typography variant="body1">{notification.message}</Typography>
        </Box>
      ))}
    </Paper>
  );
};

export default FloatingNotifications;
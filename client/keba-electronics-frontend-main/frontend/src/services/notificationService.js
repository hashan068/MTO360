// services/notificationService.js
import api from '../api';

const getNotifications = async () => {
  try {
    const response = await api.get('/api/notifications/notifications/');
    return response.data;
  } catch (error) {
    console.error('Error fetching notifications:', error);
    throw error;
  }
};

const markAsRead = async (notificationId) => {
  try {
    const response = await api.patch(`/api/notifications/notifications/${notificationId}/`, { read: true });
    return response.data;
  } catch (error) {
    console.error('Error marking notification as read:', error);
    throw error;
  }
};

export default { getNotifications, markAsRead };
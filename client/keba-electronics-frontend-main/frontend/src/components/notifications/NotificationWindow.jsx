// components/NotificationWindow.jsx
import React from 'react';
import notificationService from '../../services/notificationService';
import dayjs from 'dayjs';
import '../../styles/NotificationWindow.css';

const NotificationWindow = ({ onClose }) => {
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

  const handleMarkAsRead = async (notificationId) => {
    try {
      await notificationService.markAsRead(notificationId);
      setNotifications((prevNotifications) =>
        prevNotifications.map((notification) =>
          notification.id === notificationId
            ? { ...notification, read: true }
            : notification
        )
      );
    } catch (err) {
      console.error("Failed to mark notification as read:", err);
    }
  };

  return (
    <div className="notification-window">
      <div className="notification-header">
        <h3>Notifications</h3>
        <button onClick={onClose}>Close</button>
      </div>
      {error && <p className="error">{error}</p>}
      <ul>
        {notifications.map((notification) => (
          <li
            key={notification.id}
            className={`notification-item ${
              notification.read ? "read" : "unread"
            }`}
            onClick={() => handleMarkAsRead(notification.id)}
          >
            <div className="notification-message">{notification.message}</div>
            <div className="notification-timestamp">
              {dayjs(notification.timestamp).format("MMMM D, YYYY h:mm A")}
            </div>
            {notification.read ? (
              <span className="read-indicator">&#10003;</span>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default NotificationWindow;
import React, { useEffect, useState } from 'react';
import notificationService from '../services/notificationService';

const Notifications = () => {
    const [notifications, setNotifications] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
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
        <div>
            <h2>Notifications</h2>
            {error && <p className="error">{error}</p>}
            <ul>
                {notifications.map(notification => (
                    <li key={notification.id}>
                        {notification.message} - {new Date(notification.timestamp).toLocaleString()}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Notifications;

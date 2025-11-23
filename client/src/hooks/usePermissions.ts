import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface UserPermissions {
  user_id: number;
  permissions: string[];
  is_superuser: boolean;
}

export const usePermissions = () => {
  const [permissions, setPermissions] = useState<string[]>([]);
  const [isSuperuser, setIsSuperuser] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPermissions = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      const userId = localStorage.getItem('user_id');

      if (!userId) {
        throw new Error('User not authenticated');
      }

      const response = await axios.get<UserPermissions>(
        `${API_BASE_URL}/api/auth/users/${userId}/permissions`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setPermissions(response.data.permissions);
      setIsSuperuser(response.data.is_superuser);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch permissions');
      console.error('Error fetching permissions:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const hasPermission = useCallback(
    (permission: string): boolean => {
      return isSuperuser || permissions.includes(permission);
    },
    [permissions, isSuperuser]
  );

  const hasAnyPermission = useCallback(
    (requiredPermissions: string[]): boolean => {
      return isSuperuser || requiredPermissions.some(p => permissions.includes(p));
    },
    [permissions, isSuperuser]
  );

  const hasAllPermissions = useCallback(
    (requiredPermissions: string[]): boolean => {
      return isSuperuser || requiredPermissions.every(p => permissions.includes(p));
    },
    [permissions, isSuperuser]
  );

  useEffect(() => {
    fetchPermissions();
  }, [fetchPermissions]);

  return {
    permissions,
    isSuperuser,
    loading,
    error,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    refetch: fetchPermissions,
  };
};

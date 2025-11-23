import React, { ReactNode } from 'react';
import { usePermissions } from '../hooks/usePermissions';
import { Lock } from 'lucide-react';

interface ProtectedActionProps {
  permission?: string;
  anyPermissions?: string[];
  allPermissions?: string[];
  children: ReactNode;
  fallback?: ReactNode;
  showLocked?: boolean;
}

/**
 * Component to protect UI elements based on user permissions
 * 
 * Usage:
 * <ProtectedAction permission="production.schedule.create">
 *   <button>Create Schedule</button>
 * </ProtectedAction>
 */
const ProtectedAction: React.FC<ProtectedActionProps> = ({
  permission,
  anyPermissions,
  allPermissions,
  children,
  fallback,
  showLocked = false,
}) => {
  const { hasPermission, hasAnyPermission, hasAllPermissions, loading } = usePermissions();

  if (loading) {
    return null;
  }

  let hasAccess = false;

  if (permission) {
    hasAccess = hasPermission(permission);
  } else if (anyPermissions && anyPermissions.length > 0) {
    hasAccess = hasAnyPermission(anyPermissions);
  } else if (allPermissions && allPermissions.length > 0) {
    hasAccess = hasAllPermissions(allPermissions);
  } else {
    // No permission specified, allow access
    hasAccess = true;
  }

  if (hasAccess) {
    return <>{children}</>;
  }

  if (fallback) {
    return <>{fallback}</>;
  }

  if (showLocked) {
    return (
      <div className="relative inline-block">
        <div className="opacity-50 pointer-events-none">
          {children}
        </div>
        <div className="absolute inset-0 flex items-center justify-center">
          <Lock className="w-4 h-4 text-gray-500" />
        </div>
      </div>
    );
  }

  return null;
};

export default ProtectedAction;

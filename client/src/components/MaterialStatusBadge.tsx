import React from 'react';
import { CheckCircle, XCircle, Clock } from 'lucide-react';

interface MaterialStatusBadgeProps {
  canSchedule: boolean;
  estimatedReadyDate?: string;
  blockingReason?: string;
  showDetails?: boolean;
}

/**
 * Badge component to display material availability status
 * 
 * Usage:
 * <MaterialStatusBadge 
 *   canSchedule={true} 
 *   showDetails={true}
 * />
 */
const MaterialStatusBadge: React.FC<MaterialStatusBadgeProps> = ({
  canSchedule,
  estimatedReadyDate,
  blockingReason,
  showDetails = false,
}) => {
  if (canSchedule) {
    return (
      <div className="flex items-center gap-2">
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">
          <CheckCircle className="w-3 h-3" />
          Materials Ready
        </span>
        {showDetails && (
          <span className="text-xs text-gray-600 dark:text-gray-400">
            All components available
          </span>
        )}
      </div>
    );
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
    });
  };

  if (estimatedReadyDate) {
    return (
      <div className="flex items-center gap-2">
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400">
          <Clock className="w-3 h-3" />
          Materials Pending
        </span>
        {showDetails && (
          <span className="text-xs text-gray-600 dark:text-gray-400">
            Expected: {formatDate(estimatedReadyDate)}
          </span>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1">
      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400 w-fit">
        <XCircle className="w-3 h-3" />
        Materials Unavailable
      </span>
      {showDetails && blockingReason && (
        <span className="text-xs text-red-600 dark:text-red-400">
          {blockingReason}
        </span>
      )}
    </div>
  );
};

export default MaterialStatusBadge;


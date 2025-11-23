import React from 'react';
import { useMaterialAvailability } from '@/hooks/useMaterialAvailability';
import MaterialStatusBadge from '@/components/MaterialStatusBadge';

interface MaterialStatusCellProps {
  moId: number;
}

const MaterialStatusCell: React.FC<MaterialStatusCellProps> = ({ moId }) => {
  const { validation, loading } = useMaterialAvailability(moId);

  if (loading) {
    return <span className="text-gray-400 text-sm">Checking...</span>;
  }

  if (!validation) {
    return <span className="text-gray-400 text-sm">N/A</span>;
  }

  return (
    <MaterialStatusBadge
      canSchedule={validation.can_schedule}
      estimatedReadyDate={validation.estimated_ready_date}
      blockingReason={validation.blocking_reason}
      showDetails={false}
    />
  );
};

export default MaterialStatusCell;

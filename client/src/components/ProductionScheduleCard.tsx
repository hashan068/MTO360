import React from 'react';
import { Calendar, Clock, Factory, Package, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { useProductionSchedule, ManufacturingOrderInfo } from '../hooks/useProductionSchedule';

interface ProductionScheduleCardProps {
  salesOrderId: number;
}

const ProductionScheduleCard: React.FC<ProductionScheduleCardProps> = ({ salesOrderId }) => {
  const { schedule, loading, error } = useProductionSchedule(salesOrderId);

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 text-red-600">
          <XCircle className="w-5 h-5" />
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (!schedule || !schedule.has_production) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 text-gray-500">
          <Factory className="w-5 h-5" />
          <p className="text-sm">No production scheduled yet</p>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100 dark:bg-green-900/20';
      case 'in_production':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20';
      case 'blocked':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20';
      case 'scheduled':
        return 'text-purple-600 bg-purple-100 dark:bg-purple-900/20';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-700';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'blocked':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not scheduled';
    return new Date(dateString).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Factory className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Production Schedule
            </h3>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1 ${getStatusColor(schedule.overall_status)}`}>
            {getStatusIcon(schedule.overall_status)}
            {schedule.overall_status.replace('_', ' ').toUpperCase()}
          </span>
        </div>
      </div>

      {/* Delivery Date */}
      {schedule.estimated_delivery_date && (
        <div className="p-6 bg-blue-50 dark:bg-blue-900/10 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <Calendar className="w-5 h-5 text-blue-600" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Estimated Delivery</p>
              <p className="text-lg font-semibold text-blue-600">
                {formatDate(schedule.estimated_delivery_date)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Manufacturing Orders */}
      <div className="p-6">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
          Manufacturing Orders ({schedule.total_mos})
        </h4>
        <div className="space-y-3">
          {schedule.manufacturing_orders.map((mo: ManufacturingOrderInfo) => (
            <div
              key={mo.mo_id}
              className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Package className="w-4 h-4 text-gray-500" />
                  <span className="font-medium text-gray-900 dark:text-white">
                    {mo.mo_number}
                  </span>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(mo.status)}`}>
                  {mo.status.replace('_', ' ')}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600 dark:text-gray-400">Quantity</p>
                  <p className="font-medium text-gray-900 dark:text-white">{mo.quantity} units</p>
                </div>
                {mo.scheduled_start && (
                  <div>
                    <p className="text-gray-600 dark:text-gray-400">Scheduled Start</p>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {formatDate(mo.scheduled_start)}
                    </p>
                  </div>
                )}
                {mo.scheduled_end && (
                  <div>
                    <p className="text-gray-600 dark:text-gray-400">Scheduled End</p>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {formatDate(mo.scheduled_end)}
                    </p>
                  </div>
                )}
                {mo.total_scheduled_duration_minutes && (
                  <div>
                    <p className="text-gray-600 dark:text-gray-400">Duration</p>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {Math.round(mo.total_scheduled_duration_minutes / 60)} hours
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ProductionScheduleCard;

# Frontend Integration Examples

This document provides examples of how to integrate the newly created components into your application.

## 1. Notification Bell in App Header

Add the notification bell to your main app layout:

```tsx
// In your App.tsx or Layout component
import NotificationBell from './components/NotificationBell';

function AppLayout() {
  return (
    <header className="flex items-center justify-between p-4 bg-white shadow">
      <h1>MTO360</h1>
      
      <div className="flex items-center gap-4">
        {/* Other header items */}
        <NotificationBell />
      </div>
    </header>
  );
}
```

## 2. Production Schedule Card in Sales Order Details

Add the production schedule card to your sales order detail page:

```tsx
// In your SalesOrderDetail.tsx component
import ProductionScheduleCard from './components/ProductionScheduleCard';

function SalesOrderDetail({ orderId }: { orderId: number }) {
  return (
    <div className="space-y-6">
      {/* Other SO details */}
      
      <ProductionScheduleCard salesOrderId={orderId} />
    </div>
  );
}
```

## 3. Permission Guards for Sensitive Actions

Protect UI elements based on user permissions:

```tsx
// In your scheduling or manufacturing components
import ProtectedAction from './components/ProtectedAction';

function SchedulingPage() {
  return (
    <div>
      {/* Anyone can view */}
      <h1>Production Schedule</h1>
      
      {/* Only users with permission can create */}
      <ProtectedAction permission="production.schedule.create">
        <button className="btn-primary">Auto-Schedule</button>
      </ProtectedAction>
      
      {/* Require any of multiple permissions */}
      <ProtectedAction anyPermissions={["production.schedule.update", "production.schedule.delete"]}>
        <button className="btn-secondary">Reschedule</button>
      </ProtectedAction>
      
      {/* Show locked state instead of hiding */}
      <ProtectedAction permission="production.operation.block" showLocked>
        <button className="btn-danger">Block Operation</button>
      </ProtectedAction>
    </div>
  );
}
```

## 4. Material Availability Indicators

Show material status in manufacturing order lists or detail views:

```tsx
// In your ManufacturingOrderList.tsx or MODetail.tsx
import { useMaterialAvailability } from './hooks/useMaterialAvailability';
import MaterialStatusBadge from './components/MaterialStatusBadge';

function ManufacturingOrderRow({ moId }: { moId: number }) {
  const { validation, loading } = useMaterialAvailability(moId);
  
  return (
    <tr>
      <td>MO-{moId}</td>
      <td>
        {loading ? (
          <span className="text-gray-400">Loading...</span>
        ) : validation ? (
          <MaterialStatusBadge
            canSchedule={validation.can_schedule}
            estimatedReadyDate={validation.estimated_ready_date}
            blockingReason={validation.blocking_reason}
            showDetails={true}
          />
        ) : null}
      </td>
    </tr>
  );
}
```

## 5. Combined Example: Full Scheduling Page

Here's how all components work together:

```tsx
import React from 'react';
import ProtectedAction from './components/ProtectedAction';
import MaterialStatusBadge from './components/MaterialStatusBadge';
import { useMaterialAvailability } from './hooks/useMaterialAvailability';

function SchedulingPage() {
  const moId = 123;
  const { validation } = useMaterialAvailability(moId);
  
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Manufacturing Order {moId}</h1>
        
        {validation && (
          <MaterialStatusBadge
            canSchedule={validation.can_schedule}
            estimatedReadyDate={validation.estimated_ready_date}
            blockingReason={validation.blocking_reason}
            showDetails={true}
          />
        )}
      </div>
      
      <div className="flex gap-4">
        <ProtectedAction permission="production.schedule.create">
          <button
            className="btn-primary"
            disabled={!validation?.can_schedule}
          >
            Auto-Schedule
          </button>
        </ProtectedAction>
        
        <ProtectedAction permission="production.schedule.update">
          <button className="btn-secondary">
            Reschedule
          </button>
        </ProtectedAction>
      </div>
    </div>
  );
}
```

## Environment Variables

Make sure you have set the API base URL in your `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Authentication

All hooks expect an `access_token` and `user_id` to be stored in localStorage:

```typescript
// After login
localStorage.setItem('access_token', token);
localStorage.setItem('user_id', userId);
```

## Auto-Polling

The `useNotifications` hook automatically polls for new notifications every 30 seconds. You can adjust this interval in the hook if needed.

# Frontend Components Documentation

## Overview

This directory contains React components and hooks for the Production Scheduling Integration features.

## Components

### NotificationBell
**Location:** `src/components/NotificationBell.tsx`

Displays a bell icon with an unread notification count badge. Toggles the NotificationPanel on click.

**Props:** None

**Usage:**
```tsx
<NotificationBell />
```

---

### NotificationPanel
**Location:** `src/components/NotificationPanel.tsx`

A dropdown panel displaying all notifications with severity icons, timestamps, and actions.

**Props:**
- `onClose: () => void` - Callback when panel should close

**Features:**
- Click notification to navigate to action URL
- Mark individual notifications as read
- Mark all as read
- Auto-close on outside click
- Severity-based color coding

---

### ProtectedAction
**Location:** `src/components/ProtectedAction.tsx`

Wrapper component that shows/hides child elements based on user permissions.

**Props:**
- `permission?: string` - Single permission to check
- `anyPermissions?: string[]` - Show if user has ANY of these permissions
- `allPermissions?: string[]` - Show if user has ALL of these permissions
- `children: ReactNode` - Content to protect
- `fallback?: ReactNode` - Content to show if access denied
- `showLocked?: boolean` - Show locked icon overlay instead of hiding

**Usage:**
```tsx
<ProtectedAction permission="production.schedule.create">
  <button>Create Schedule</button>
</ProtectedAction>
```

---

### ProductionScheduleCard
**Location:** `src/components/ProductionScheduleCard.tsx`

Displays production schedule information for a sales order, including all manufacturing orders, statuses, and estimated delivery date.

**Props:**
- `salesOrderId: number` - Sales order ID to fetch schedule for

**Features:**
- Shows all MOs with status badges
- Displays estimated delivery date
- Color-coded overall status
- Scheduled start/end dates
- Production duration

---

### MaterialStatusBadge
**Location:** `src/components/MaterialStatusBadge.tsx`

Visual indicator for material availability status.

**Props:**
- `canSchedule: boolean` - Whether materials are available
- `estimatedReadyDate?: string` - When materials will be ready
- `blockingReason?: string` - Reason if materials unavailable
- `showDetails?: boolean` - Show additional details

**Statuses:**
- ✅ **Materials Ready** (Green) - All components available
- ⏰ **Materials Pending** (Yellow) - Components on order, shows estimated date
- ❌ **Materials Unavailable** (Red) - Missing components with reason

---

## Hooks

### useNotifications
**Location:** `src/hooks/useNotifications.ts`

Fetches and manages user notifications.

**Returns:**
- `notifications: Notification[]` - Array of notifications
- `unreadCount: number` - Count of unread notifications
- `loading: boolean` - Loading state
- `error: string | null` - Error message if any
- `fetchNotifications: () => Promise<void>` - Manually refetch
- `markAsRead: (id: number) => Promise<void>` - Mark one as read
- `markAllAsRead: () => Promise<void>` - Mark all as read

**Auto-polling:** Fetches every 30 seconds

---

### usePermissions
**Location:** `src/hooks/usePermissions.ts`

Fetches and checks user permissions.

**Returns:**
- `permissions: string[]` - Array of permission codes
- `isSuperuser: boolean` - Whether user is superuser
- `loading: boolean` - Loading state
- `error: string | null` - Error message if any
- `hasPermission: (permission: string) => boolean` - Check single permission
- `hasAnyPermission: (permissions: string[]) => boolean` - Check if has any
- `hasAllPermissions: (permissions: string[]) => boolean` - Check if has all
- `refetch: () => Promise<void>` - Manually refetch

---

### useProductionSchedule
**Location:** `src/hooks/useProductionSchedule.ts`

Fetches production schedule for a sales order.

**Parameters:**
- `salesOrderId?: number` - Sales order ID

**Returns:**
- `schedule: ProductionSchedule | null` - Schedule data
- `loading: boolean` - Loading state
- `error: string | null` - Error message if any
- `refetch: () => Promise<void>` - Manually refetch

---

### useMaterialAvailability
**Location:** `src/hooks/useMaterialAvailability.ts`

Checks material availability for a manufacturing order.

**Parameters:**
- `manufacturingOrderId?: number` - MO ID

**Returns:**
- `validation: MaterialValidation | null` - Validation result
- `loading: boolean` - Loading state
- `error: string | null` - Error message if any
- `refetch: () => Promise<void>` - Manually refetch

---

## Permission Codes

### Production Scheduling
- `production.schedule.view` - View schedules
- `production.schedule.create` - Create/auto-schedule
- `production.schedule.update` - Update/reschedule
- `production.schedule.delete` - Delete schedules

### Shop Floor
- `production.operation.view` - View operations
- `production.operation.start` - Start operations
- `production.operation.complete` - Complete operations
- `production.operation.pause` - Pause operations
- `production.operation.block` - Block operations
- `production.operation.unblock` - Unblock operations

### Work Centers
- `production.workcenter.view` - View work centers
- `production.workcenter.manage` - Manage work centers

---

## Styling

All components use Tailwind CSS with dark mode support. Colors and styles follow the application's design system.

## Error Handling

All hooks include error states. Components gracefully handle loading and error states with appropriate UI feedback.

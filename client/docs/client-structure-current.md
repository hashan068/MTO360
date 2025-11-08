## Client Structure Audit (Post-Refactor)

### Feature Modules
- **Auth**
  - `src/features/auth/api/index.ts`
  - `src/features/auth/hooks/useAuth.ts`
  - `src/features/auth/pages/LoginPage.tsx`
  - `src/features/auth/routes/ProtectedRoute.tsx`
  - `src/features/auth/store/authStore.ts`
- **Dashboard**
  - `src/features/dashboard/pages/DashboardPage.tsx`
- **Inventory**
  - `src/features/inventory/api/index.ts`
  - `src/features/inventory/pages/*.tsx`
  - `src/features/inventory/routes/index.tsx`
  - `src/features/inventory/types/index.ts`
- **Manufacturing**
  - `src/features/manufacturing/api/index.ts`
  - `src/features/manufacturing/pages/*.tsx`
  - `src/features/manufacturing/routes/index.tsx`
  - `src/features/manufacturing/types/index.ts`
- **Sales**
  - `src/features/sales/api/index.ts`
  - `src/features/sales/pages/*.tsx`
  - `src/features/sales/routes/index.tsx`
  - `src/features/sales/types/index.ts`

### Shared Modules
- **Components**
  - `src/shared/components/layout/*`
  - `src/shared/components/feedback/FullScreenLoader.tsx`
- **State**
  - `src/shared/state/uiStore.ts`
- **API Infrastructure**
  - `src/shared/api/client.ts`
- **Hooks**
  - `src/shared/hooks/useApiMutation.ts`
  - `src/shared/hooks/useDebouncedValue.ts`
- **Constants & Utilities**
  - `src/shared/constants/storage.ts`
  - `src/shared/utils/format.ts`
  - `src/shared/utils/storage.ts`
- **Theme**
  - `src/shared/theme/index.ts`
- **Types**
  - `src/shared/types/{api,common,index,user}.ts`
- **Pages**
  - `src/shared/pages/NotFoundPage.tsx`

### Entry & Routing
- `src/App.tsx`
- `src/main.tsx`
- `src/routes/index.tsx`

### Tooling & Configuration Updates
- `tsconfig.json` path aliases for `@features/*` and `@shared/*`
- `vite.config.ts` alias mirroring for dev/build


<!-- c22eb314-9eac-4b6c-8f7f-d058f254b540 24935805-1b2b-4e9f-ae17-513d4fb58777 -->
# Django to FastAPI DDD Migration Plan

## Overview

Migrate the Django REST Framework backend to FastAPI with Domain-Driven Design architecture. The project currently has 4 Django apps that will be converted to DDD modules: Inventory, Sales, Manufacturing, and Notifications.

## Current State Analysis

**Django Apps:**

- Inventory: Components, Suppliers, Purchase Requisitions, Purchase Orders, Transactions
- Sales: Customers, Products, RFQs, Quotations, Sales Orders
- Manufacturing: Manufacturing Orders, Material Requisitions, Bill of Materials
- Notifications: User notifications

**Tech Stack:**

- Django REST Framework with ViewSets
- Django Models (PostgreSQL)
- JWT Authentication (djangorestframework-simplejwt)
- Djoser for user management

## Migration Strategy

### Phase 1: Project Structure Setup (2-3 hours)

1. Create FastAPI project structure under `backend/app/`
2. Set up configuration (`config/`)
3. Set up database connection (SQLAlchemy)
4. Set up middleware (CORS, authentication)
5. Create base FastAPI application (`main.py`)

### Phase 2: Shared Infrastructure (3-4 hours)

1. **Database Models (`app/models/`):**

   - Convert Django models to SQLAlchemy models
   - Maintain relationships and constraints
   - Add Alembic for migrations

2. **Schemas (`app/schemas/`):**

   - Convert Django serializers to Pydantic schemas
   - Create request/response models

3. **Authentication (`app/middleware/` or `app/auth/`):**

   - Implement JWT authentication
   - Create FastAPI dependencies for auth
   - Migrate user authentication from Django

4. **Database Config (`app/config/`):**

   - Database connection setup
   - Session management
   - Environment configuration

### Phase 3: Module Migration (16-20 hours per module)

For each module (Inventory, Sales, Manufacturing, Notifications):

#### 3.1 Infrastructure Layer (`infra/repositories/`)

- Convert Django ORM queries to SQLAlchemy
- Create repository classes for each entity
- Implement data access patterns

#### 3.2 Domain Layer (`domain/`)

- Define repository interfaces (Protocols)
- Define domain entities (if needed)
- Define value objects and business rules

#### 3.3 Application Layer (`application/services/`)

- Extract business logic from views
- Create service classes
- Implement transaction management
- Add dependency injection with Protocol interfaces

#### 3.4 API Layer (`api/`)

- Convert ViewSets to FastAPI routers
- Create endpoint handlers
- Maintain existing API paths for backward compatibility
- Add request/response validation

#### 3.5 Module Registration

- Create module router aggregator
- Register module in `module_registry`
- Update `main.py` to include module routers

### Phase 4: Testing & Validation (4-6 hours)

1. Test all API endpoints
2. Verify database operations
3. Test authentication/authorization
4. Validate business logic
5. Performance testing

### Phase 5: Documentation (2-3 hours)

1. Create module README files
2. Document API endpoints
3. Update migration guides
4. Create setup instructions

## Detailed Implementation Plan

### Step 1: Create Base Structure

```
backend/app/
├── __init__.py
├── main.py
├── config/
│   ├── __init__.py
│   ├── database.py
│   ├── settings.py
├── models/
│   ├── __init__.py
│   ├── base.py
│   ├── inventory.py
│   ├── sales.py
│   ├── manufacturing.py
│   └── notifications.py
├── schemas/
│   ├── __init__.py
│   ├── inventory.py
│   ├── sales.py
│   ├── manufacturing.py
│   └── notifications.py
├── middleware/
│   ├── __init__.py
│   ├── auth.py
│   └── cors.py
├── dependencies.py
└── modules/
    ├── __init__.py
    ├── README.md
    ├── inventory/
    ├── sales/
    ├── manufacturing/
    └── notifications/
```

### Step 2: Convert Models

For each Django model:

- Convert to SQLAlchemy declarative model
- Maintain field types and constraints
- Preserve relationships (Foreign Keys, Many-to-Many)
- Add indexes and constraints
- Create Alembic migration

### Step 3: Convert Schemas

For each Django serializer:

- Create Pydantic BaseModel for requests
- Create Pydantic BaseModel for responses
- Add validation rules
- Handle nested serialization

### Step 4: Create Module Structure

For each module (e.g., Inventory):

```
modules/inventory/
├── __init__.py
├── README.md
├── api/
│   ├── __init__.py
│   ├── router.py
│   ├── components.py
│   ├── suppliers.py
│   ├── purchase_requisitions.py
│   └── purchase_orders.py
├── application/
│   ├── __init__.py
│   └── services/
│       ├── __init__.py
│       ├── component_service.py
│       ├── supplier_service.py
│       └── purchase_service.py
├── domain/
│   ├── __init__.py
│   └── interfaces.py
└── infra/
    ├── __init__.py
    └── repositories/
        ├── __init__.py
        ├── component_repo.py
        ├── supplier_repo.py
        └── purchase_repo.py
```

### Step 5: Migrate Business Logic

- Extract logic from Django views to async services
- Move database queries to async repositories
- Use async SQLAlchemy sessions for all database operations
- Implement Protocol-based interfaces (async methods)
- Add dependency injection with async support
- Use `async def` for all I/O-bound operations

### Step 6: Convert API Endpoints

- Convert ViewSet actions to FastAPI route handlers
- Maintain API path compatibility
- Add proper error handling
- Add request/response validation

## Key Files to Create/Modify

### New Files:

- `backend/app/main.py` - FastAPI application
- `backend/app/config/database.py` - SQLAlchemy setup
- `backend/app/config/settings.py` - Configuration
- `backend/app/middleware/auth.py` - JWT authentication
- `backend/app/dependencies.py` - FastAPI dependencies
- `backend/app/modules/__init__.py` - Module registry
- Module structure for each domain (Inventory, Sales, Manufacturing, Notifications)

### Files to Convert:

- Django models → SQLAlchemy models
- Django serializers → Pydantic schemas
- Django ViewSets → FastAPI routers
- Django utils → Application services

## Dependencies to Add

```toml
[project]
dependencies = [
    "fastapi[standard]>=0.121.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.13.0",
    "psycopg2-binary>=2.9.9",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.6",
]
```

## Migration Order

1. **Inventory Module** (most independent)

   - Components, Suppliers, Purchase Requisitions, Purchase Orders

2. **Sales Module** (depends on Inventory for products)

   - Customers, Products, RFQs, Quotations, Sales Orders

3. **Manufacturing Module** (depends on Sales and Inventory)

   - Manufacturing Orders, Material Requisitions, BOMs

4. **Notifications Module** (used by all modules)

   - User notifications

## API Compatibility

Maintain existing API paths:

- `/api/inventory/*` → `modules/inventory/api/*`
- `/api/sales/*` → `modules/sales/api/*`
- `/api/manufacturing/*` → `modules/manufacturing/api/*`
- `/api/notifications/*` → `modules/notifications/api/*`

## Authentication Migration

- Convert JWT token generation to python-jose
- Create FastAPI dependency for authentication
- Migrate user model or keep Django user model
- Implement token refresh endpoint

## Database Migration

- Option A: Create Alembic migrations from SQLAlchemy models
- Option B: Use Django migrations as reference for Alembic
- Maintain data integrity during migration

## Testing Strategy

- Unit tests for services (with mocked repositories)
- Integration tests for API endpoints
- Database transaction tests
- Authentication/authorization tests

## Risk Mitigation

- Maintain Django project until FastAPI is fully tested
- Create comprehensive test suite
- Document all API changes
- Plan rollback strategy

## Estimated Timeline

- Phase 1 (Structure): 2-3 hours
- Phase 2 (Shared Infrastructure): 3-4 hours
- Phase 3 (Module Migration): 64-80 hours (16-20 hours × 4 modules)
- Phase 4 (Testing): 4-6 hours
- Phase 5 (Documentation): 2-3 hours

**Total: 75-96 hours (~10-12 days)**

## Success Criteria

- All API endpoints functional
- Database operations working correctly
- Authentication/authorization working
- Business logic preserved
- Performance acceptable
- Code follows DDD principles
- Comprehensive documentation
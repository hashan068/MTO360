# MTO360 FastAPI Backend

FastAPI backend with Domain-Driven Design (DDD) architecture.

## Architecture

The application follows Domain-Driven Design principles with clear layer separation:

- **API Layer** - REST endpoints (FastAPI routers)
- **Application Layer** - Business logic (services)
- **Domain Layer** - Domain interfaces (Protocols)
- **Infrastructure Layer** - Data access (repositories)

## Modules

- **Inventory** - Components, Suppliers, Purchase Requisitions, Purchase Orders
- **Sales** - Customers, Products, RFQs, Quotations, Sales Orders  
- **Manufacturing** - Manufacturing Orders, Material Requisitions, BOMs
- **Notifications** - User notifications

## Setup

### 1. Install Dependencies

```bash
pip install -e .
# or
uv pip install -e .
```

### 2. Configure Environment

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mto360
SECRET_KEY=your-secret-key-here
DEBUG=True
```

Or configure individual database settings:

```env
DATABASE_NAME=mto360
DATABASE_USER=your_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
SECRET_KEY=your-secret-key-here
```

### 3. Initialize Database

```bash
# Create Alembic migrations
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

Or create tables directly (development only):

```python
from app.config.database import init_db
import asyncio

asyncio.run(init_db())
```

### 4. Run Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

The API uses JWT authentication:

1. Login: `POST /api/token` with `username` and `password`
2. Use the `access` token in the `Authorization: Bearer <token>` header
3. Refresh token: `POST /api/token/refresh` with `refresh_token`

## Project Structure

```
backend/app/
├── api/                    # Shared API routes (auth)
├── config/                 # Configuration
├── models/                 # SQLAlchemy models
├── schemas/                # Pydantic schemas
├── middleware/             # Middleware (auth, CORS)
├── modules/                # Domain modules
│   ├── inventory/         # Inventory module (complete)
│   ├── sales/             # Sales module (structure)
│   ├── manufacturing/     # Manufacturing module (structure)
│   └── notifications/     # Notifications module (structure)
└── main.py                # FastAPI application
```

## Migration from Django

This FastAPI application is a migration from Django REST Framework:

- Django models → SQLAlchemy models (async)
- Django serializers → Pydantic schemas
- Django ViewSets → FastAPI routers
- Django ORM → SQLAlchemy async repositories

## Next Steps

1. Complete Sales module implementation
2. Complete Manufacturing module implementation
3. Complete Notifications module implementation
4. Add comprehensive tests
5. Set up Alembic migrations properly
6. Add API documentation

## Notes

- The Inventory module is fully implemented following DDD patterns
- Other modules have structure in place and can be completed following the same pattern
- All database operations are async
- Authentication uses JWT tokens


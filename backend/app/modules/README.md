# Modular Architecture Guide

Welcome to the modular architecture documentation for the MTO360 application.

## Overview

This directory contains all application modules organized following Domain-Driven Design (DDD) principles with clear layer separation.

### Architecture Principles

1. **Bounded Contexts** - Each module represents a distinct business domain
2. **Layer Separation** - Clear boundaries between API, Application, Domain, and Infrastructure
3. **Dependency Inversion** - Services depend on abstractions (Protocols), not concrete implementations
4. **Explicit Exports** - All layers define `__all__` for clean imports
5. **Dynamic Registration** - Modules auto-register via `module_registry`

## Current Modules

- **Inventory** - Components, Suppliers, Purchase Requisitions, Purchase Orders
- **Sales** - Customers, Products, RFQs, Quotations, Sales Orders
- **Manufacturing** - Manufacturing Orders, Material Requisitions, Bill of Materials
- **Notifications** - User notifications

## Directory Structure

Each module follows this structure:

```
{module_name}/
├── __init__.py                 # Module exports (router)
├── README.md                   # Module documentation
├── api/                        # REST API layer (controllers)
│   ├── __init__.py            # Export router
│   ├── router.py              # Aggregate subrouters
│   └── {resource}.py          # Resource endpoints
├── application/                # Application layer (business logic)
│   ├── __init__.py
│   └── services/              # Business services
│       ├── __init__.py        # Export all services
│       └── {service}.py
├── domain/                     # Domain layer (core business)
│   ├── __init__.py
│   └── interfaces.py          # Repository interfaces (Protocols)
└── infra/                      # Infrastructure layer
    ├── __init__.py            # Export repositories
    └── repositories/          # Data access
        ├── __init__.py        # Export all repos
        └── {repo}.py
```


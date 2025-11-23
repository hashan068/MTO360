"""
Modular architecture for domain-driven design.
Each module represents a bounded context with its own
api, application, domain, and infrastructure layers.
"""
from importlib import import_module
from typing import Dict, Optional, TypedDict


class ModuleSpec(TypedDict, total=False):
    router: object
    services: Dict[str, object]


module_registry: Dict[str, ModuleSpec] = {}


def register_module(
    name: str,
    router_path: str,
    router_attr: str = "router",
    services: Optional[Dict[str, str]] = None,
) -> None:
    """
    Register a module with its router and optional services.
    
    Args:
        name: Module name
        router_path: Module path to router (e.g., "app.modules.inventory.api.router")
        router_attr: Router attribute name (default: "router")
        services: Optional dict mapping service names to dotted paths
    """
    mod = import_module(router_path)
    router = getattr(mod, router_attr)
    spec: ModuleSpec = {"router": router}
    
    if services:
        resolved: Dict[str, object] = {}
        for key, dotted in services.items():
            pkg, attr = dotted.rsplit(":", 1)
            resolved[key] = getattr(import_module(pkg), attr)
        spec["services"] = resolved
    
    module_registry[name] = spec


# Modules will be registered here as they are created
register_module("inventory", "app.modules.inventory.api.router", "router")
register_module("sales", "app.modules.sales.api.router", "router")
register_module("manufacturing", "app.modules.manufacturing.api.router", "router")
register_module("notifications", "app.modules.notifications.api.router", "router")

# Material availability router (additional inventory module route)
try:
    from app.modules.inventory.api.material_availability import router as material_router
    module_registry["material-availability"] = {"router": material_router}
except ImportError as e:
    print(f"Warning: Could not import material_availability router: {e}")

# Production integration router (additional sales module route)
try:
    from app.modules.sales.api.production_integration import router as prod_integration_router
    module_registry["production-integration"] = {"router": prod_integration_router}
except ImportError as e:
    print(f"Warning: Could not import production_integration router: {e}")


"""
FastAPI application main entry point
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.config.database import init_db, close_db
from app.modules import module_registry
from app.api.auth import router as auth_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting up...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="MTO360 API",
    description="Manufacturing to Order 360 - FastAPI Backend",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
# Handle CORS_ORIGINS as string or list
cors_origins = settings.CORS_ORIGINS
if isinstance(cors_origins, str):
    cors_origins = [origin.strip() for origin in cors_origins.split(",")]
elif not isinstance(cors_origins, list):
    cors_origins = list(cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "MTO360 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include authentication routes
app.include_router(auth_router)


def include_module_routes():
    """Include all module routers"""
    loaded_routes = []
    failed_routes = []
    
    for name, spec in module_registry.items():
        try:
            app.include_router(spec["router"])
            loaded_routes.append(name)
            logger.info(f"✅ {name} module registered")
        except Exception as e:
            failed_routes.append((name, str(e)))
            logger.error(f"❌ Failed to register module {name}: {e}")
    
    if failed_routes:
        logger.warning(f"Failed routes: {[name for name, _ in failed_routes]}")
    
    return loaded_routes, failed_routes


# Include module routes
include_module_routes()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


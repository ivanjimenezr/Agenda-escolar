"""
FastAPI main application entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.config import settings
from src.infrastructure.database import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Runs on startup and shutdown.
    """
    # Startup: Initialize database
    print("🚀 Starting up Agenda Escolar Pro API...")
    print(f"📊 Environment: {settings.environment}")
    print(f"🔧 Debug mode: {settings.debug}")

    # Uncomment to auto-create tables (use migrations in production)
    # init_db()

    yield

    # Shutdown: Close database connections
    print("👋 Shutting down...")
    close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="API REST para gestión de agenda escolar con IA",
    version=settings.api_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# Configure CORS
# Note: Make sure to set CORS_ORIGINS environment variable in production
# with your frontend domain (e.g., "https://yourapp.vercel.app")
cors_origins = settings.cors_origins_list
print(f"🌐 CORS origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["Content-Type", "Authorization"],
    max_age=3600,  # Cache preflight requests for 1 hour
)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.app_name,
        "version": settings.api_version,
        "status": "running",
        "environment": settings.environment,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
    }


@app.get("/api/v1/ping")
async def ping():
    """Simple ping endpoint for testing."""
    return {"message": "pong"}


# Import and include routers
from src.infrastructure.api.routes import active_modules, auth, dinners, events, exams, menus, students, subjects, users

app.include_router(auth.router)  # auth.py ya tiene el prefijo /api/v1/auth
app.include_router(users.router, prefix="/api/v1")
app.include_router(students.router, prefix="/api/v1")
app.include_router(menus.router, prefix="/api/v1")
app.include_router(active_modules.router, prefix="/api/v1")
app.include_router(dinners.router, prefix="/api/v1")
app.include_router(subjects.router, prefix="/api/v1")
app.include_router(exams.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )

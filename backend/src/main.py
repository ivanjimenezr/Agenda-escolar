"""
FastAPI main application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.infrastructure.config import settings
from src.infrastructure.database import init_db, close_db


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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


# Import and include routers here when created
# Example:
# from src.infrastructure.api.routes import students, subjects, exams
# app.include_router(students.router, prefix="/api/v1/students", tags=["students"])
# app.include_router(subjects.router, prefix="/api/v1/subjects", tags=["subjects"])
# app.include_router(exams.router, prefix="/api/v1/exams", tags=["exams"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )

"""
DealFinder FastAPI Application
Main entry point for the Filter Management API
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as api_router
from src.data.database import close_async_engine
from src.services.keepa_client import close_keepa_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    # Startup
    print("🚀 DealFinder API starting...")

    yield

    # Shutdown
    print("🔄 DealFinder API shutting down...")
    await close_async_engine()
    await close_keepa_client()
    print("✅ Cleanup complete")


# Create FastAPI application
app = FastAPI(
    title="DealFinder API",
    description="""
    ## Deal-Finder Bot API

    Manage deal filters, generate reports, and track analytics.

    ### Features
    - **Filter Management**: Create, update, delete deal filters
    - **Report History**: View generated deal reports
    - **Click Tracking**: Track user interactions with deals
    - **GDPR Compliance**: User consent and deletion support

    ### Authentication
    For demo purposes, use the `X-User-ID` header to specify a user.
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint - API documentation"""
    return {
        "service": "DealFinder API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)

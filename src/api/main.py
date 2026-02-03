"""
FastAPI application for Amazon Arbitrage Tracker.
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Arbitrage Tracker API...")
    yield
    logger.info("Shutting down Arbitrage Tracker API...")


app = FastAPI(
    title="Amazon Arbitrage Tracker API",
    description="REST API for accessing Amazon product price data and arbitrage opportunities",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


from src.api.routes import products, arbitrage, health

app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(arbitrage.router, prefix="/arbitrage", tags=["Arbitrage"])
app.include_router(health.router, prefix="/health", tags=["Health"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Amazon Arbitrage Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
    }


def main():
    """Main entry point."""
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))

    logger.info(f"Starting API server on {host}:{port}")

    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()

"""
Keeper System API - Main FastAPI Application
With PostgreSQL persistence and real-time price monitoring
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

from services.database import (
    init_db,
    create_watch,
    get_user_watches,
    update_watch_price,
    get_pending_alerts,
    mark_alert_sent,
)
from services.keepa_api import KeepaAPIClient, TokenLimitError, NoDealAccessError
from services.keepa_api import get_keepa_client
from scheduler import run_immediate_check, check_single_asin


# Pydantic Models
class WatchCreateRequest(BaseModel):
    """Request model for creating a new watch"""

    asin: str = Field(
        ...,
        min_length=10,
        max_length=10,
        description="Amazon Product ASIN (10 characters)",
    )
    target_price: float = Field(..., gt=0, description="Target price to trigger alert")


class WatchResponse(BaseModel):
    """Response model for watch data"""

    id: str
    asin: str
    target_price: float
    current_price: Optional[float] = None
    status: str
    last_checked_at: Optional[str] = None
    created_at: str


class WatchDeleteResponse(BaseModel):
    """Response for watch deletion"""

    status: str
    message: str


class DealSearchRequest(BaseModel):
    """Request model for deal search"""

    categories: List[str] = ["16142011"]
    min_discount: int = Field(default=20, ge=0, le=100)
    max_discount: int = Field(default=80, ge=0, le=100)
    min_price: float = Field(default=0, ge=0)
    max_price: float = Field(default=500, ge=0)
    min_rating: float = Field(default=4.0, ge=0, le=5.0)


class DealResponse(BaseModel):
    """Response model for a deal"""

    asin: str
    title: str
    current_price: float
    list_price: float
    discount_percent: float
    rating: float
    reviews: int
    prime_eligible: bool
    url: str
    deal_score: float


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: str
    tokens_available: int
    watches_count: int


class PriceCheckRequest(BaseModel):
    """Request model for manual price check"""

    asin: str = Field(..., min_length=10, max_length=10)


class PriceCheckResponse(BaseModel):
    """Response for manual price check"""

    asin: str
    title: Optional[str] = None
    current_price: float
    list_price: float
    rating: float
    category: str
    timestamp: str


class TriggerCheckResponse(BaseModel):
    """Response for triggering a price check"""

    status: str
    watches_checked: int
    price_changes: int
    alerts_triggered: int
    timestamp: str


# FastAPI App
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    print("🚀 Keeper System starting...")
    await init_db()
    print("✅ Database initialized")
    print("✅ Keeper System ready!")
    yield


app = FastAPI(
    title="Keeper System API",
    description="Amazon Price Monitoring & Deal Finder with Persistent Storage",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health & Status Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    client = get_keepa_client()
    token_status = client.get_token_status()

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "tokens_available": token_status.get("tokens_available", 0),
        "watches_count": 0,  # Will be updated with actual count
    }


@app.get("/api/v1/status")
async def get_status():
    """Get detailed system status"""
    client = get_keepa_client()
    token_status = client.get_token_status()
    rate_limit = client.check_rate_limit()

    return {
        "system": "healthy",
        "version": "2.0.0",
        "token_bucket": token_status,
        "rate_limit": rate_limit,
        "timestamp": datetime.utcnow().isoformat(),
    }


# Watch CRUD Endpoints
@app.get("/api/v1/watches", response_model=List[WatchResponse])
async def list_watches(user_id: str = Query(..., description="User ID")):
    """
    List all watches for a user.
    Returns current price status for each watched product.
    """
    watches = await get_user_watches(user_id)

    return [
        {
            "id": str(w.id),
            "asin": w.asin,
            "target_price": w.target_price,
            "current_price": w.current_price,
            "status": w.status.value if hasattr(w.status, "value") else str(w.status),
            "last_checked_at": w.last_checked_at.isoformat()
            if w.last_checked_at
            else None,
            "created_at": w.created_at.isoformat(),
        }
        for w in watches
    ]


@app.post("/api/v1/watches", response_model=WatchResponse, status_code=201)
async def create_watch(
    request: WatchCreateRequest, user_id: str = Query(..., description="User ID")
):
    """
    Create a new price watch for an Amazon product.
    Automatically fetches current price and starts monitoring.
    """
    # Validate ASIN format
    if len(request.asin) != 10:
        raise HTTPException(
            status_code=400, detail="Invalid ASIN format. Must be 10 characters."
        )

    if request.target_price <= 0:
        raise HTTPException(
            status_code=400, detail="Target price must be greater than 0."
        )

    try:
        # Fetch current price from Keepa
        client = get_keepa_client()
        product_data = await client.query_product(request.asin)

        current_price = product_data.get("current_price", 0) if product_data else None

        # Create watch in database
        watch = await create_watch(
            user_id=user_id,
            asin=request.asin,
            target_price=request.target_price,
            current_price=current_price,
        )

        return {
            "id": str(watch.id),
            "asin": watch.asin,
            "target_price": watch.target_price,
            "current_price": watch.current_price,
            "status": watch.status.value
            if hasattr(watch.status, "value")
            else str(watch.status),
            "last_checked_at": watch.last_checked_at.isoformat()
            if watch.last_checked_at
            else None,
            "created_at": watch.created_at.isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating watch: {str(e)}")


@app.delete("/api/v1/watches/{watch_id}", response_model=WatchDeleteResponse)
async def delete_watch(watch_id: str, user_id: str = Query(..., description="User ID")):
    """Delete a watch (mark as inactive)"""
    # For now, just return success
    # In production, you'd query and update the database
    return {"status": "deleted", "message": f"Watch {watch_id} deleted successfully"}


# Price Check Endpoints
@app.post("/api/v1/price/check", response_model=PriceCheckResponse)
async def check_price(request: PriceCheckRequest):
    """
    Manually check the current price of a product.
    Returns detailed product information.
    """
    try:
        client = get_keepa_client()
        product_data = await client.query_product(request.asin)

        if not product_data:
            raise HTTPException(
                status_code=404, detail=f"Product {request.asin} not found"
            )

        return {
            "asin": request.asin,
            "title": product_data.get("title"),
            "current_price": product_data.get("current_price", 0),
            "list_price": product_data.get("list_price", 0),
            "rating": product_data.get("rating", 0),
            "category": product_data.get("category", ""),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking price: {str(e)}")


@app.post("/api/v1/price/check-all", response_model=TriggerCheckResponse)
async def trigger_price_check_all():
    """
    Trigger an immediate price check for all active watches.
    This will check prices, update database, and trigger alerts if needed.
    """
    try:
        result = await run_immediate_check()

        return {
            "status": "completed",
            "watches_checked": result.get("total", 0),
            "price_changes": result.get("price_changes", 0),
            "alerts_triggered": result.get("alerts_triggered", 0),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error running price check: {str(e)}"
        )


# Deals Endpoints
@app.post("/api/v1/deals/search", response_model=List[DealResponse])
async def search_deals(request: DealSearchRequest):
    """Search for deals matching the specified criteria"""
    from services.keepa_api import DealFilters

    try:
        client = get_keepa_client()
        filters = DealFilters(
            page=0,
            domain_id=3,  # Germany
            min_rating=int(request.min_rating),
            min_reviews=10,
        )

        # Note: Full deal search with all filters would need additional
        # implementation in the KeepaAPIClient.search_deals method

        result = client.search_deals(filters)

        deals = []
        for deal in result.get("deals", []):
            discount = deal.get("discount_percent", 0)

            # Apply request filters
            if (
                discount >= request.min_discount
                and discount <= request.max_discount
                and deal.get("current_price", 0) >= request.min_price
                and deal.get("current_price", 0) <= request.max_price
            ):
                deal_score = discount * 0.4 + deal.get("rating", 0) * 20 * 0.6

                deals.append(
                    {
                        "asin": deal.get("asin", ""),
                        "title": deal.get("title", ""),
                        "current_price": deal.get("current_price", 0),
                        "list_price": deal.get("list_price", 0),
                        "discount_percent": discount,
                        "rating": deal.get("rating", 0),
                        "reviews": deal.get("reviews", 0),
                        "prime_eligible": deal.get("prime_eligible", False),
                        "url": deal.get("url", ""),
                        "deal_score": deal_score,
                    }
                )

        return deals[:15]

    except TokenLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except NoDealAccessError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching deals: {str(e)}")


# Rate Limit Endpoints
@app.get("/api/v1/tokens")
async def get_token_status():
    """Get current token bucket status"""
    client = get_keepa_client()
    return client.get_token_status()


@app.get("/api/v1/rate-limit")
async def get_rate_limit():
    """Get rate limit information from Keepa API"""
    client = get_keepa_client()
    return client.check_rate_limit()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
Filter Management API Routes
FastAPI endpoints for filter CRUD operations
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database import get_async_session
from src.data.entities import User
from src.data.repositories import (
    FilterRepository,
    ReportRepository,
    ClickRepository,
    UserRepository,
)
from src.domain.models import (
    CreateFilterRequest,
    FilterConfig,
    EmailSchedule,
    DealSearchResult,
    SearchResponse,
    ClickTrackingRequest,
    ClickTrackingResponse,
    DealReport,
    DealFilter,
)


router = APIRouter(prefix="/api/v1", tags=["Filters"])


async def get_current_user(
    x_user_id: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Get current user from header (simplified auth)"""
    if not x_user_id:
        # For demo: create or get a demo user
        repo = UserRepository(session)
        user = await repo.get_by_email("demo@dealfinder.app")
        if not user:
            user = await repo.create("demo@dealfinder.app")
        return user

    try:
        user_id = UUID(x_user_id)
        repo = UserRepository(session)
        user = await repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")


@router.post("/filters", response_model=dict, status_code=201)
async def create_filter(
    request: CreateFilterRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Create a new deal filter

    Creates a filter with the specified criteria for finding deals.
    The filter will be used for daily email reports if email_enabled is true.
    """
    repo = FilterRepository(session)

    try:
        filter_obj = await repo.create(
            user_id=user.id,
            name=request.name,
            categories=request.categories,
            price_min=float(request.min_price),
            price_max=float(request.max_price),
            discount_min=request.min_discount,
            discount_max=request.max_discount,
            min_rating=float(request.min_rating),
            min_review_count=request.min_review_count,
            max_sales_rank=request.max_sales_rank,
            email_enabled=request.email_enabled,
            email_time=request.email_time,
        )

        return {
            "id": str(filter_obj.id),
            "status": "created",
            "message": "Filter created successfully!",
            "meta": {
                "created_at": filter_obj.created_at.isoformat(),
                "email_enabled": filter_obj.email_enabled,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/filters", response_model=List[dict])
async def list_filters(
    active_only: bool = Query(True, description="Only return active filters"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    List all filters for the current user

    Returns a list of all filters created by the user.
    """
    repo = FilterRepository(session)
    filters = await repo.get_by_user(user.id, active_only=active_only)

    return [
        {
            "id": str(f.id),
            "name": f.name,
            "categories": f.categories,
            "price_range": f.price_range,
            "discount_range": f.discount_range,
            "min_rating": float(f.min_rating) if f.min_rating else None,
            "min_review_count": f.min_review_count,
            "max_sales_rank": f.max_sales_rank,
            "email_enabled": f.email_enabled,
            "email_schedule": f.email_schedule,
            "is_active": f.is_active,
            "created_at": f.created_at.isoformat(),
            "updated_at": f.updated_at.isoformat(),
        }
        for f in filters
    ]


@router.get("/filters/{filter_id}", response_model=dict)
async def get_filter(
    filter_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get a specific filter by ID

    Returns the full configuration of a single filter.
    """
    repo = FilterRepository(session)
    filter_obj = await repo.get_by_id(filter_id)

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    if filter_obj.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "id": str(filter_obj.id),
        "name": filter_obj.name,
        "categories": filter_obj.categories,
        "price_range": filter_obj.price_range,
        "discount_range": filter_obj.discount_range,
        "min_rating": float(filter_obj.min_rating) if filter_obj.min_rating else None,
        "min_review_count": filter_obj.min_review_count,
        "max_sales_rank": filter_obj.max_sales_rank,
        "email_enabled": filter_obj.email_enabled,
        "email_schedule": filter_obj.email_schedule,
        "is_active": filter_obj.is_active,
        "created_at": filter_obj.created_at.isoformat(),
        "updated_at": filter_obj.updated_at.isoformat(),
    }


@router.patch("/filters/{filter_id}", response_model=dict)
async def update_filter(
    filter_id: UUID,
    name: Optional[str] = None,
    categories: Optional[List[str]] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_discount: Optional[int] = None,
    max_discount: Optional[int] = None,
    min_rating: Optional[float] = None,
    email_enabled: Optional[bool] = None,
    email_time: Optional[str] = None,
    is_active: Optional[bool] = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Update a filter configuration

    Partial update - only provided fields will be changed.
    """
    repo = FilterRepository(session)
    filter_obj = await repo.get_by_id(filter_id)

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    if filter_obj.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    updated = await repo.update(
        filter_id=filter_id,
        name=name,
        categories=categories,
        price_min=min_price,
        price_max=max_price,
        discount_min=min_discount,
        discount_max=max_discount,
        min_rating=min_rating,
        email_enabled=email_enabled,
        email_time=email_time,
        is_active=is_active,
    )

    if not updated:
        raise HTTPException(status_code=400, detail="Update failed")

    return {
        "id": str(updated.id),
        "status": "updated",
        "message": "Filter updated successfully",
        "updated_at": updated.updated_at.isoformat(),
    }


@router.delete("/filters/{filter_id}", response_model=dict)
async def delete_filter(
    filter_id: UUID,
    hard_delete: bool = Query(False, description="Permanently delete filter"),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Delete a filter

    By default, this soft-deletes (deactivates) the filter.
    Set hard_delete=true to permanently remove it.
    """
    repo = FilterRepository(session)
    filter_obj = await repo.get_by_id(filter_id)

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    if filter_obj.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if hard_delete:
        await repo.delete(filter_id)
        message = "Filter permanently deleted"
    else:
        await repo.deactivate(filter_id)
        message = "Filter deactivated (soft deleted)"

    return {"status": "success", "message": message}


@router.get("/filters/{filter_id}/reports", response_model=List[dict])
async def list_reports(
    filter_id: UUID,
    limit: int = Query(10, ge=1, le=50),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get report history for a filter

    Returns the most recent generated reports for this filter.
    """
    filter_repo = FilterRepository(session)
    filter_obj = await filter_repo.get_by_id(filter_id)

    if not filter_obj:
        raise HTTPException(status_code=404, detail="Filter not found")

    if filter_obj.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    report_repo = ReportRepository(session)
    reports = await report_repo.get_by_filter(filter_id, limit=limit)

    return [
        {
            "id": str(r.id),
            "deal_count": r.deal_count,
            "generated_at": r.generated_at.isoformat(),
            "email_sent_at": r.email_sent_at.isoformat() if r.email_sent_at else None,
            "email_status": r.email_status,
            "open_count": r.open_count,
            "click_count": r.click_count,
        }
        for r in reports
    ]


# ============ Analytics Endpoints ============


@router.post("/analytics/click", response_model=ClickTrackingResponse)
async def track_click(
    request: ClickTrackingRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Track a deal click

    Records when a user clicks on a deal from a report.
    """
    click_repo = ClickRepository(session)

    click = await click_repo.create(
        user_id=user.id,
        report_id=request.report_id,
        asin=request.asin,
        utm_source=request.utm_source,
        utm_medium=request.utm_medium,
    )

    # Increment report click count
    report_repo = ReportRepository(session)
    await report_repo.increment_clicks(request.report_id)

    return ClickTrackingResponse(status="tracked", click_id=click.id)


@router.get("/analytics/clicks", response_model=List[dict])
async def get_clicks(
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get user's click history

    Returns the most recent deals the user has clicked on.
    """
    repo = ClickRepository(session)
    clicks = await repo.get_user_clicks(user.id, limit=limit)

    return [
        {
            "id": str(c.id),
            "asin": c.asin,
            "report_id": str(c.report_id),
            "clicked_at": c.clicked_at.isoformat(),
            "utm_source": c.utm_source,
            "utm_medium": c.utm_medium,
        }
        for c in clicks
    ]


# ============ Health Check ============


@router.get("/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "service": "dealfinder-api",
        "timestamp": datetime.utcnow().isoformat(),
    }

"""
Products API endpoints.
"""

import sys
import os
import logging
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from src.consumer.indexer import ElasticsearchIndexer, create_indexer

logger = logging.getLogger(__name__)

router = APIRouter()


def get_indexer() -> ElasticsearchIndexer:
    """Dependency for Elasticsearch indexer."""
    return create_indexer()


class ProductSummary(BaseModel):
    """Product summary for list responses."""

    asin: str = ""
    title: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    current_prices: dict = {}
    best_margin: Optional[float] = None
    best_source: Optional[str] = None
    target_marketplace: str = "DE"
    estimated_profit: Optional[float] = None
    last_updated: Optional[str] = None


class ProductDetail(ProductSummary):
    """Product detail with full information."""

    brand: Optional[str] = None
    product_url: Optional[str] = None
    price_history: dict = {}
    is_active: bool = True


class Pagination(BaseModel):
    """Pagination information."""

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ProductListResponse(BaseModel):
    """Response for product list endpoint."""

    success: bool = True
    data: dict = {}
    filters_applied: dict = {}


class ProductDetailResponse(BaseModel):
    """Response for product detail endpoint."""

    success: bool = True
    data: Optional[ProductDetail] = None


class ErrorResponse(BaseModel):
    """Error response."""

    success: bool = False
    error: dict = {}


def calculate_best_opportunity(product: dict, target_marketplace: str = "DE") -> dict:
    """Calculate best arbitrage opportunity for a product."""
    current_prices = product.get("current_prices", {})
    target_price = current_prices.get(target_marketplace)

    if not target_price:
        return {}

    best_margin = 0
    best_source = None
    best_profit = 0

    for source_mp, source_price in current_prices.items():
        if source_mp == target_marketplace or source_price is None:
            continue

        profit = target_price - source_price
        margin = (profit / target_price) * 100 if target_price > 0 else 0

        if margin > best_margin:
            best_margin = margin
            best_source = source_mp
            best_profit = profit

    return {
        "best_margin": round(best_margin, 2) if best_margin else None,
        "best_source": best_source,
        "estimated_profit": round(best_profit, 2) if best_profit else None,
    }


@router.get("/", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    marketplace: Optional[str] = Query(
        None, regex="^(DE|IT|ES|UK|FR)$", description="Target marketplace"
    ),
    min_margin: float = Query(0, ge=0, le=100, description="Minimum margin percentage"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum target price"),
    category: Optional[str] = Query(None, description="Category filter"),
    sort_by: str = Query("updated_desc", regex="^(margin|price|updated)_(desc|asc)$"),
    indexer: ElasticsearchIndexer = Depends(get_indexer),
) -> ProductListResponse:
    """
    List products with optional filtering and pagination.
    """
    try:
        offset = (page - 1) * page_size

        must_clauses = [{"term": {"is_active": True}}]
        filters_applied = {}

        if marketplace:
            filters_applied["target_marketplace"] = marketplace

        sort_map = {
            "margin_desc": [{"best_margin": {"order": "desc"}}],
            "margin_asc": [{"best_margin": {"order": "asc"}}],
            "price_desc": [{"current_prices.DE": {"order": "desc"}}],
            "price_asc": [{"current_prices.DE": {"order": "asc"}}],
            "updated_desc": [{"last_updated": {"order": "desc"}}],
            "updated_asc": [{"last_updated": {"order": "asc"}}],
        }

        sort = sort_map.get(sort_by, [{"last_updated": {"order": "desc"}}])

        query = {"bool": {"must": must_clauses}}

        result = indexer.search(
            query=query,
            size=page_size,
            from_=offset,
            sort=sort,
        )

        products = result.get("hits", [])
        total = result.get("total", 0)

        enriched_products = []
        for product in products:
            opportunity = calculate_best_opportunity(product, marketplace or "DE")

            if min_margin > 0 and (opportunity.get("best_margin", 0) or 0) < min_margin:
                continue

            if max_price and product.get("current_prices", {}).get("DE", 0) > max_price:
                continue

            enriched = {
                "asin": product.get("asin"),
                "title": product.get("title"),
                "image_url": product.get("image_url"),
                "category": product.get("category"),
                "current_prices": product.get("current_prices", {}),
                "best_margin": opportunity.get("best_margin"),
                "best_source": opportunity.get("best_source"),
                "target_marketplace": marketplace or "DE",
                "estimated_profit": opportunity.get("estimated_profit"),
                "last_updated": product.get("last_updated"),
            }
            enriched_products.append(enriched)

        total_pages = (total + page_size - 1) // page_size

        pagination = Pagination(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )

        return ProductListResponse(
            success=True,
            data={
                "products": enriched_products,
                "pagination": pagination.dict(),
            },
            filters_applied=filters_applied,
        )

    except Exception as e:
        logger.error(f"Error listing products: {e}")
        return ProductListResponse(
            success=False,
            data={"products": [], "pagination": {}},
            filters_applied={"error": str(e)},
        )


@router.get("/{asin}", response_model=ProductDetailResponse)
async def get_product(
    asin: str,
    indexer: ElasticsearchIndexer = Depends(get_indexer),
) -> ProductDetailResponse:
    """
    Get product details by ASIN.
    """
    try:
        if not asin or len(asin) != 10:
            raise HTTPException(status_code=400, detail="Invalid ASIN format")

        product = indexer.get_product(asin)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        opportunity = calculate_best_opportunity(product)

        detail = ProductDetail(
            asin=product.get("asin"),
            title=product.get("title"),
            brand=product.get("brand"),
            image_url=product.get("image_url"),
            category=product.get("category"),
            current_prices=product.get("current_prices", {}),
            best_margin=opportunity.get("best_margin"),
            best_source=opportunity.get("best_source"),
            estimated_profit=opportunity.get("estimated_profit"),
            last_updated=product.get("last_updated"),
            product_url=product.get("product_url"),
            price_history=product.get("price_history", {}),
            is_active=product.get("is_active", True),
        )

        return ProductDetailResponse(success=True, data=detail)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {asin}: {e}")
        return ProductDetailResponse(success=False, data=None)

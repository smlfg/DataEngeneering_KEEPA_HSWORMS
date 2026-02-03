"""
Arbitrage API endpoints.
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.consumer.indexer import ElasticsearchIndexer, create_indexer
from src.arbitrage.calculator import ArbitrageCalculator, create_calculator

router = APIRouter()


def get_indexer() -> ElasticsearchIndexer:
    """Dependency for Elasticsearch indexer."""
    return create_indexer()


def get_calculator() -> ArbitrageCalculator:
    """Dependency for arbitrage calculator."""
    return create_calculator()


class ArbitrageOpportunityModel(BaseModel):
    """Arbitrage opportunity model."""

    asin: str
    title: Optional[str] = None
    image_url: Optional[str] = None
    source_marketplace: str
    target_marketplace: str
    source_price: float
    target_price: float
    margin: float
    profit: float
    estimated_fees: float
    net_profit: float
    confidence: str
    last_updated: Optional[str] = None


class ArbitrageSummary(BaseModel):
    """Summary statistics for arbitrage."""

    total_count: int = 0
    avg_margin: Optional[float] = None
    avg_profit: Optional[float] = None
    highest_margin: Optional[float] = None
    highest_profit: Optional[float] = None


class ArbitrageListResponse(BaseModel):
    """Response for arbitrage list endpoint."""

    success: bool = True
    data: dict = {}


def find_opportunities_for_product(
    product: dict,
    calculator: ArbitrageCalculator,
    target_marketplace: str,
    min_margin: float,
    min_profit: float,
) -> List[dict]:
    """Find all arbitrage opportunities for a product."""
    current_prices = product.get("current_prices", {})
    target_price = current_prices.get(target_marketplace)

    if not target_price:
        return []

    opportunities = []
    target_price_val = float(target_price)

    for source_mp, source_price in current_prices.items():
        if source_mp == target_marketplace:
            continue
        if source_price is None:
            continue

        source_price_val = float(source_price)
        margin, profit = calculator.calculate_margin(source_price_val, target_price_val)

        if margin < min_margin:
            continue

        if profit < min_profit:
            continue

        fees = calculator.calculate_fees(target_price_val)
        net_profit = profit - fees
        confidence = calculator.calculate_confidence(source_price_val).value

        opportunity = {
            "asin": product.get("asin"),
            "title": product.get("title"),
            "image_url": product.get("image_url"),
            "source_marketplace": source_mp,
            "target_marketplace": target_marketplace,
            "source_price": round(source_price_val, 2),
            "target_price": round(target_price_val, 2),
            "margin": round(margin, 2),
            "profit": round(profit, 2),
            "estimated_fees": round(fees, 2),
            "net_profit": round(net_profit, 2),
            "confidence": confidence,
            "last_updated": product.get("last_updated"),
        }
        opportunities.append(opportunity)

    return sorted(opportunities, key=lambda x: x["margin"], reverse=True)


@router.get("/", response_model=ArbitrageListResponse)
async def list_arbitrage(
    min_margin: float = Query(
        15, ge=0, le=100, description="Minimum profit margin percentage"
    ),
    min_profit: float = Query(10, ge=0, description="Minimum absolute profit in EUR"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results"),
    source_marketplace: Optional[str] = Query(
        None, description="Filter by source marketplace (comma-separated: IT,ES,UK,FR)"
    ),
    target_marketplace: str = Query(
        "DE", regex="^(DE|IT|ES|UK|FR)$", description="Target marketplace"
    ),
    indexer: ElasticsearchIndexer = Depends(get_indexer),
    calculator: ArbitrageCalculator = Depends(get_calculator),
) -> ArbitrageListResponse:
    """
    List arbitrage opportunities filtered by criteria.
    """
    try:
        result = indexer.search(
            query={"term": {"is_active": True}},
            size=500,
        )

        products = result.get("hits", [])
        all_opportunities = []

        for product in products:
            opportunities = find_opportunities_for_product(
                product,
                calculator,
                target_marketplace,
                min_margin,
                min_profit,
            )
            all_opportunities.extend(opportunities)

        if source_marketplace:
            allowed_sources = [s.strip() for s in source_marketplace.split(",")]
            all_opportunities = [
                o
                for o in all_opportunities
                if o["source_marketplace"] in allowed_sources
            ]

        all_opportunities = all_opportunities[:limit]

        margins = [o["margin"] for o in all_opportunities]
        profits = [o["profit"] for o in all_opportunities]

        summary = ArbitrageSummary(
            total_count=len(all_opportunities),
            avg_margin=sum(margins) / len(margins) if margins else None,
            avg_profit=sum(profits) / len(profits) if profits else None,
            highest_margin=max(margins) if margins else None,
            highest_profit=max(profits) if profits else None,
        )

        return ArbitrageListResponse(
            success=True,
            data={
                "opportunities": all_opportunities,
                "summary": summary.dict(),
            },
        )

    except Exception as e:
        logger.error(f"Error listing arbitrage: {e}")
        return ArbitrageListResponse(
            success=False,
            data={"opportunities": [], "summary": {}},
        )


@router.get("/top", response_model=ArbitrageListResponse)
async def get_top_arbitrage(
    limit: int = Query(10, ge=1, le=100, description="Number of top opportunities"),
    target_marketplace: str = Query(
        "DE", regex="^(DE|IT|ES|UK|FR)$", description="Target marketplace"
    ),
    indexer: ElasticsearchIndexer = Depends(get_indexer),
    calculator: ArbitrageCalculator = Depends(get_calculator),
) -> ArbitrageListResponse:
    """
    Get top arbitrage opportunities with highest margins.
    """
    return await list_arbitrage(
        min_margin=0,
        min_profit=0,
        limit=limit,
        target_marketplace=target_marketplace,
        indexer=indexer,
        calculator=calculator,
    )

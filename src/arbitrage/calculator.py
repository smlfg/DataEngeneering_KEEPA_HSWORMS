"""
Arbitrage margin calculation engine.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ConfidenceLevel(str, Enum):
    """Confidence level for arbitrage opportunities."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ArbitrageOpportunity:
    """Represents a single arbitrage opportunity."""

    asin: str
    title: Optional[str] = None
    image_url: Optional[str] = None
    source_marketplace: str = ""
    target_marketplace: str = ""
    source_price: float = 0.0
    target_price: float = 0.0
    margin: float = 0.0
    profit: float = 0.0
    estimated_fees: float = 0.0
    net_profit: float = 0.0
    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    priority: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asin": self.asin,
            "title": self.title,
            "image_url": self.image_url,
            "source_marketplace": self.source_marketplace,
            "target_marketplace": self.target_marketplace,
            "source_price": self.source_price,
            "target_price": self.target_price,
            "margin": self.margin,
            "profit": self.profit,
            "estimated_fees": self.estimated_fees,
            "net_profit": self.net_profit,
            "confidence": self.confidence.value,
            "priority": self.priority,
            "timestamp": self.timestamp,
        }


class ArbitrageCalculator:
    """
    Calculates arbitrage margins and detects opportunities.

    Formulas:
    - Gross Margin = (Target Price - Source Price) / Target Price * 100
    - Gross Profit = Target Price - Source Price
    - Estimated Fees = Target Price * FBA Fee Percentage (default 15%)
    - Net Profit = Gross Profit - Estimated Fees
    - Confidence = 1.0 - (Price Volatility / Average Price)
    """

    DEFAULT_FBA_FEE_PERCENTAGE = 0.15
    CONFIDENCE_THRESHOLDS = {
        "high": 0.9,
        "medium": 0.7,
        "low": 0.0,
    }

    def __init__(
        self,
        fba_fee_percentage: float = DEFAULT_FBA_FEE_PERCENTAGE,
        min_margin_threshold: float = 15.0,
    ):
        self.fba_fee_percentage = fba_fee_percentage
        self.min_margin_threshold = min_margin_threshold

    def calculate_margin(
        self,
        source_price: float,
        target_price: float,
    ) -> Tuple[float, float]:
        """
        Calculate gross margin and profit.

        Args:
            source_price: Price at source marketplace (EUR)
            target_price: Price at target marketplace (EUR)

        Returns:
            Tuple of (margin_percentage, profit_euro)
        """
        if target_price <= 0:
            return 0.0, 0.0

        profit = target_price - source_price
        margin = (profit / target_price) * 100

        return margin, profit

    def calculate_fees(self, target_price: float) -> float:
        """
        Calculate estimated Amazon fees.

        Args:
            target_price: Sale price at target marketplace

        Returns:
            Estimated fees in EUR
        """
        return target_price * self.fba_fee_percentage

    def calculate_net_profit(
        self,
        source_price: float,
        target_price: float,
    ) -> float:
        """
        Calculate net profit after fees.

        Args:
            source_price: Price at source marketplace
            target_price: Price at target marketplace

        Returns:
            Net profit in EUR
        """
        gross_profit = target_price - source_price
        fees = self.calculate_fees(target_price)

        return gross_profit - fees

    def calculate_confidence(
        self,
        current_price: float,
        avg_price: Optional[float] = None,
    ) -> ConfidenceLevel:
        """
        Calculate confidence level based on price stability.

        Args:
            current_price: Current price
            avg_price: Average price (optional)

        Returns:
            Confidence level (high/medium/low)
        """
        if avg_price is None or avg_price <= 0:
            return ConfidenceLevel.MEDIUM

        volatility = abs(current_price - avg_price) / avg_price
        confidence_score = 1.0 - volatility

        if confidence_score >= self.CONFIDENCE_THRESHOLDS["high"]:
            return ConfidenceLevel.HIGH
        elif confidence_score >= self.CONFIDENCE_THRESHOLDS["medium"]:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def calculate_priority(
        self,
        margin: float,
        net_profit: float,
        confidence: ConfidenceLevel,
    ) -> int:
        """
        Calculate priority score for an opportunity.

        Priority formula:
        Priority = margin_weight * margin + profit_weight * normalized_profit + confidence_bonus

        Args:
            margin: Gross margin percentage
            net_profit: Net profit in EUR
            confidence: Confidence level

        Returns:
            Priority score (0-100)
        """
        margin_weight = 0.6
        profit_weight = 0.4

        normalized_profit = min(net_profit / 100, 1.0)  # Cap at 100 EUR

        confidence_bonus = {
            ConfidenceLevel.HIGH: 20,
            ConfidenceLevel.MEDIUM: 10,
            ConfidenceLevel.LOW: 0,
        }[confidence]

        priority = (
            (margin_weight * min(margin, 100))
            + (profit_weight * normalized_profit * 100)
            + confidence_bonus
        )

        return min(int(priority), 100)

    def find_opportunities(
        self,
        current_prices: Dict[str, Union[float, None]],
        target_marketplace: str = "DE",
        exclude_source: Optional[List[str]] = None,
    ) -> List["ArbitrageOpportunity"]:
        """
        Find all arbitrage opportunities for a product.

        Args:
            current_prices: Dictionary of marketplace -> price
            target_marketplace: Target marketplace code
            exclude_source: Marketplaces to exclude as source

        Returns:
            List of ArbitrageOpportunity objects
        """
        if exclude_source is None:
            exclude_source = [target_marketplace]

        target_price = current_prices.get(target_marketplace)
        if target_price is None or target_price <= 0:
            return []

        opportunities = []

        for source_mp, source_price in current_prices.items():
            if source_mp in exclude_source:
                continue
            if source_price is None or source_price <= 0:
                continue

            margin, profit = self.calculate_margin(source_price, target_price)

            if margin < self.min_margin_threshold:
                continue

            fees = self.calculate_fees(target_price)
            net_profit = profit - fees
            confidence = self.calculate_confidence(source_price)
            priority = self.calculate_priority(margin, net_profit, confidence)

            opportunity = ArbitrageOpportunity(
                asin="",  # To be set by caller
                source_marketplace=source_mp,
                target_marketplace=target_marketplace,
                source_price=source_price,
                target_price=target_price,
                margin=round(margin, 2),
                profit=round(profit, 2),
                estimated_fees=round(fees, 2),
                net_profit=round(net_profit, 2),
                confidence=confidence,
                priority=priority,
            )

            opportunities.append(opportunity)

        opportunities.sort(key=lambda x: x.priority, reverse=True)

        return opportunities

    def get_best_opportunity(
        self,
        current_prices: Dict[str, Optional[float]],
        target_marketplace: str = "DE",
    ) -> Optional[ArbitrageOpportunity]:
        """
        Get the best arbitrage opportunity for a product.

        Args:
            current_prices: Dictionary of marketplace -> price
            target_marketplace: Target marketplace code

        Returns:
            Best ArbitrageOpportunity or None
        """
        opportunities = self.find_opportunities(
            current_prices,
            target_marketplace,
        )

        return opportunities[0] if opportunities else None


def create_calculator(
    fba_fee_percentage: Optional[float] = None,
    min_margin_threshold: Optional[float] = None,
) -> ArbitrageCalculator:
    """Factory function to create ArbitrageCalculator."""
    import os

    fee_pct = fba_fee_percentage or float(os.getenv("FBA_FEE_PERCENTAGE", "0.15"))
    min_margin = min_margin_threshold or float(
        os.getenv("MIN_MARGIN_THRESHOLD", "15.0")
    )

    return ArbitrageCalculator(
        fba_fee_percentage=fee_pct,
        min_margin_threshold=min_margin,
    )


if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.INFO)

    calculator = create_calculator()

    current_prices = {
        "DE": 149.99,
        "IT": 89.99,
        "ES": 92.50,
        "UK": 95.00,
        "FR": 94.00,
    }

    print("Testing Arbitrage Calculator...")
    print(f"\nCurrent Prices: {current_prices}")

    opportunities = calculator.find_opportunities(
        current_prices, target_marketplace="DE"
    )

    print(f"\nFound {len(opportunities)} opportunities:")
    for opp in opportunities:
        print(f"\n  {opp.source_marketplace} → {opp.target_marketplace}")
        print(f"  Margin: {opp.margin:.1f}%")
        print(f"  Profit: €{opp.profit:.2f}")
        print(f"  Net Profit: €{opp.net_profit:.2f}")
        print(f"  Confidence: {opp.confidence.value}")
        print(f"  Priority: {opp.priority}")

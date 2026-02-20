"""
Deal Scoring Service
Implements intelligent deal scoring based on multiple factors
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
import re


@dataclass
class ScoringResult:
    """Result of deal scoring"""

    deal_score: float  # 0-100
    breakdown: dict
    is_spam: bool
    spam_reason: Optional[str] = None


class DealScoringService:
    """
    Scores deals based on multiple factors:
    - Discount percentage (40% weight)
    - Rating quality (30% weight)
    - Sales rank popularity (20% weight)
    - Seller quality (10% weight)
    """

    # Scoring weights
    WEIGHT_DISCOUNT = 0.40
    WEIGHT_RATING = 0.30
    WEIGHT_RANK = 0.20
    WEIGHT_SELLER = 0.10

    # Constants for normalization
    MAX_DISCOUNT = 80  # 80% is considered max realistic discount
    MAX_RATING = 5.0
    MAX_SALES_RANK = 100000

    # Spam detection constants
    MIN_RATING_THRESHOLD = 3.0
    MIN_REVIEWS_FOR_HIGH_RATING = 5
    MAX_REVIEW_VELOCITY_PER_DAY = 50

    # Blacklisted seller patterns
    SPAM_SELLER_PATTERNS = [
        r"imported",
        r"wholesale",
        r"dropship",
        r"refurbished",
        r"overseas",
    ]

    def score_deal(self, deal: dict) -> ScoringResult:
        """
        Score a single deal

        Args:
            deal: Parsed deal dictionary

        Returns:
            ScoringResult with score, breakdown, and spam status
        """
        # Spam detection first
        is_spam, spam_reason = self._detect_spam(deal)

        if is_spam:
            return ScoringResult(
                deal_score=0.0,
                breakdown={
                    "discount_score": 0,
                    "rating_score": 0,
                    "rank_score": 0,
                    "seller_score": 0,
                },
                is_spam=True,
                spam_reason=spam_reason,
            )

        # Calculate individual scores
        discount_score = self._score_discount(deal.get("discount_percent", 0))
        rating_score = self._score_rating(deal.get("rating"), deal.get("review_count"))
        rank_score = self._score_rank(deal.get("sales_rank"))
        seller_score = self._score_seller(deal)

        # Calculate weighted total
        total_score = (
            discount_score * self.WEIGHT_DISCOUNT
            + rating_score * self.WEIGHT_RATING
            + rank_score * self.WEIGHT_RANK
            + seller_score * self.WEIGHT_SELLER
        )

        return ScoringResult(
            deal_score=round(total_score, 2),
            breakdown={
                "discount_score": round(discount_score, 2),
                "rating_score": round(rating_score, 2),
                "rank_score": round(rank_score, 2),
                "seller_score": round(seller_score, 2),
            },
            is_spam=False,
            spam_reason=None,
        )

    def _score_discount(self, discount_percent: int) -> float:
        """Score discount percentage (0-100)"""
        if discount_percent is None:
            return 0.0
        normalized = min(discount_percent / self.MAX_DISCOUNT, 1.0)
        return normalized * 100

    def _score_rating(
        self, rating: Optional[Decimal], review_count: Optional[int]
    ) -> float:
        """Score rating quality"""
        if rating is None:
            return 50.0  # Neutral

        rating_value = float(rating)

        # Penalize high ratings with few reviews (suspicious)
        if (
            rating_value >= 4.5
            and (review_count or 0) < self.MIN_REVIEWS_FOR_HIGH_RATING
        ):
            return float(rating_value) / self.MAX_RATING * 60  # Reduced score

        return (rating_value / self.MAX_RATING) * 100

    def _score_rank(self, sales_rank: Optional[int]) -> float:
        """Score sales rank popularity"""
        if sales_rank is None:
            return 50.0  # Neutral

        # Lower rank = higher score (more popular)
        normalized = max(0, 1 - (sales_rank / self.MAX_SALES_RANK))
        return normalized * 100

    def _score_seller(self, deal: dict) -> float:
        """Score seller quality"""
        if deal.get("is_amazon_seller"):
            return 100.0  # Amazon seller is best

        seller_name = deal.get("seller_name", "") or ""

        # Check for suspicious seller names
        for pattern in self.SPAM_SELLER_PATTERNS:
            if re.search(pattern, seller_name, re.IGNORECASE):
                return 40.0  # Penalize suspicious sellers

        return 70.0  # Neutral third-party seller

    def _detect_spam(self, deal: dict) -> tuple[bool, Optional[str]]:
        """
        Detect if deal is likely spam/dropshipper/fake

        Returns:
            (is_spam, reason) tuple
        """
        # Check rating/review mismatch
        rating = deal.get("rating")
        review_count = deal.get("review_count")

        if rating and review_count is not None:
            # 5 stars with 1 review = suspicious
            if float(rating) >= 4.8 and review_count <= 1:
                return True, "Suspicious rating: 4.8+ stars with only 1 review"

            # 5 stars with very few reviews
            if float(rating) == 5.0 and review_count < 3:
                return True, "Suspicious: Perfect rating with minimal reviews"

        # Check price inconsistency
        current_price = deal.get("current_price")
        original_price = deal.get("original_price")

        if current_price and original_price:
            if float(current_price) > float(original_price):
                return True, "Price inconsistency: Current price higher than original"

        # Check for spam patterns in seller name
        seller_name = deal.get("seller_name", "") or ""
        for pattern in self.SPAM_SELLER_PATTERNS:
            if re.search(pattern, seller_name, re.IGNORECASE):
                return True, f"Suspicious seller: '{seller_name}' matches pattern"

        # Check for zero reviews with high rating
        if review_count == 0 and rating and float(rating) >= 4.0:
            return True, "Zero reviews but 4+ stars - suspicious"

        return False, None

    def rank_deals(self, deals: list[dict]) -> list[dict]:
        """
        Rank a list of deals by their score

        Args:
            deals: List of parsed deals

        Returns:
            Deals sorted by score (descending), with scores added
        """
        scored_deals = []

        for deal in deals:
            result = self.score_deal(deal)

            if not result.is_spam:
                deal["deal_score"] = result.deal_score
                deal["score_breakdown"] = result.breakdown
                deal["is_spam"] = False
                scored_deals.append(deal)

        # Sort by score descending
        scored_deals.sort(key=lambda x: x.get("deal_score", 0), reverse=True)

        return scored_deals


# Singleton instance
_deal_scoring_service: Optional[DealScoringService] = None


def get_deal_scoring_service() -> DealScoringService:
    """Get or create deal scoring service singleton"""
    global _deal_scoring_service
    if _deal_scoring_service is None:
        _deal_scoring_service = DealScoringService()
    return _deal_scoring_service

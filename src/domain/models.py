"""
DealFinder Domain Models
Based on Bauplan IDEE 5
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator
import json


class EmailStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    BOUNCED = "BOUNCED"
    COMPLAINED = "COMPLAINED"


class GdprConsentType(str, Enum):
    MARKETING = "MARKETING"
    ANALYTICS = "ANALYTICS"
    GENERAL = "GENERAL"


class GdprStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


# ============ Value Objects ============


class PriceRange(BaseModel):
    min: Decimal = Decimal("0")
    max: Decimal = Decimal("10000")
    currency: str = "EUR"


class DiscountRange(BaseModel):
    min: int = 0
    max: int = 100


class EmailSchedule(BaseModel):
    time: str = "06:00"
    timezone: str = "Europe/Berlin"
    days: list[str] = Field(default_factory=lambda: ["MON", "TUE", "WED", "THU", "FRI"])


class FilterConfig(BaseModel):
    categories: list[str] = Field(default_factory=list)
    price_range: PriceRange = Field(default_factory=PriceRange)
    discount_range: DiscountRange = Field(default_factory=DiscountRange)
    min_rating: Decimal = Decimal("4.0")
    min_review_count: int = 10
    max_sales_rank: int = 100000


class ScoreBreakdown(BaseModel):
    discount_score: float
    rating_score: float
    rank_score: float
    seller_score: float


# ============ Domain Entities ============


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: str
    email_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    gdpr_consent_given: bool = False
    gdpr_consent_date: Optional[datetime] = None


class DealFilter(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    name: str
    config: FilterConfig = Field(default_factory=FilterConfig)
    email_enabled: bool = True
    email_schedule: EmailSchedule = Field(default_factory=EmailSchedule)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    # Convenience properties for JSON serialization
    @property
    def categories(self) -> list[str]:
        return self.config.categories

    @property
    def price_range_dict(self) -> dict:
        return self.config.price_range.model_dump()

    @property
    def discount_range_dict(self) -> dict:
        return self.config.discount_range.model_dump()


class Deal(BaseModel):
    asin: str
    title: str
    category: Optional[str] = None
    current_price: Decimal
    original_price: Optional[Decimal] = None
    discount_percent: Optional[int] = None
    rating: Optional[Decimal] = None
    review_count: Optional[int] = None
    sales_rank: Optional[int] = None
    amazon_url: Optional[str] = None
    image_url: Optional[str] = None
    seller_name: Optional[str] = None
    is_amazon_seller: Optional[bool] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class DealSnapshot(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    asin: str
    deal_score: Optional[float] = None
    score_breakdown: Optional[ScoreBreakdown] = None
    spam_flag: bool = False
    spam_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None


class DealReport(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    filter_id: UUID
    deals: list = Field(default_factory=list)
    deal_count: int = 0
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    email_sent_at: Optional[datetime] = None
    email_status: EmailStatus = EmailStatus.PENDING
    email_message_id: Optional[str] = None
    open_count: int = 0
    click_count: int = 0


class DealClick(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    report_id: UUID
    asin: str
    clicked_at: datetime = Field(default_factory=datetime.utcnow)
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None


class ReportOpen(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    report_id: UUID
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class KeepaApiLog(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    api_key_hash: Optional[str] = None
    endpoint: Optional[str] = None
    status_code: Optional[int] = None
    request_params: Optional[dict] = None
    response_summary: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GdprConsentLog(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    consent_type: GdprConsentType
    given: bool
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GdprDeletionRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    delete_personal_data: bool = True
    delete_reports: bool = True
    delete_analytics: bool = False
    status: GdprStatus = GdprStatus.PENDING


# ============ API Request/Response Models ============


class CreateFilterRequest(BaseModel):
    name: str
    categories: list[str]
    min_price: Decimal
    max_price: Decimal
    min_discount: int
    max_discount: int
    min_rating: Decimal
    min_review_count: int
    max_sales_rank: int
    email_enabled: bool = True
    email_time: str = "06:00"


class DealSearchQuery(BaseModel):
    categories: list[str]
    min_price: Decimal
    max_price: Decimal
    min_discount: int
    max_discount: int
    min_rating: Decimal
    max_sales_rank: int
    limit: int = 15
    sort_by: str = "deal_score"


class DealSearchResult(BaseModel):
    rank: int
    asin: str
    title: str
    current_price: Decimal
    original_price: Optional[Decimal]
    discount_percent: int
    rating: Optional[Decimal]
    review_count: Optional[int]
    sales_rank: Optional[int]
    deal_score: float
    amazon_url: str
    deal_reason: str


class SearchResponse(BaseModel):
    deals: list[DealSearchResult]
    total_count: int
    returned_count: int
    execution_time_ms: int
    api_calls_made: int
    cache_hit: bool


class ClickTrackingRequest(BaseModel):
    report_id: UUID
    asin: str
    utm_source: str
    utm_medium: str


class ClickTrackingResponse(BaseModel):
    status: str
    click_id: UUID

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class AgentType(str, Enum):
    PRICE_MONITOR = "price_monitor"
    DEAL_FINDER = "deal_finder"
    ALERT_DISPATCHER = "alert_dispatcher"


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


@dataclass
class PriceData:
    asin: str
    current_price: float
    target_price: float
    buy_box_seller: Optional[str] = None
    timestamp: str = ""
    alert_triggered: bool = False


@dataclass
class DealData:
    asin: str
    title: str
    current_price: float
    original_price: float
    discount_percent: float
    rating: float
    sales_rank: int
    amazon_url: str
    deal_score: float = 0.0


@dataclass
class AlertData:
    product_id: str
    product_name: str
    current_price: float
    target_price: float
    amazon_url: str
    channel: str = "email"
    sent: bool = False


@dataclass
class WorkflowState:
    workflow_id: str
    workflow_type: str
    status: WorkflowStatus = WorkflowStatus.PENDING

    products: List[PriceData] = field(default_factory=list)
    deals: List[DealData] = field(default_factory=list)
    alerts: List[AlertData] = field(default_factory=list)

    current_agent: Optional[AgentType] = None
    errors: List[Dict[str, Any]] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3

    created_at: str = ""
    updated_at: str = ""
    completed_at: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()

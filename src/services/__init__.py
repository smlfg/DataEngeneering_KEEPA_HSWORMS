# DealFinder Services
from src.services.keepa_client import (
    KeepaClient,
    get_keepa_client,
    close_keepa_client,
    KeepaApiError,
    KeepaRateLimitError,
    KeepaAuthError,
    KeepaTimeoutError,
)
from src.services.deal_scoring import (
    DealScoringService,
    get_deal_scoring_service,
    ScoringResult,
)
from src.services.report_generator import ReportGeneratorService, get_report_generator
from src.services.email_sender import (
    EmailSenderService,
    get_email_sender,
    EmailSendError,
    EmailAuthError,
    EmailRateLimitError,
    EmailSMTPError,
)

__all__ = [
    "KeepaClient",
    "get_keepa_client",
    "close_keepa_client",
    "KeepaApiError",
    "KeepaRateLimitError",
    "KeepaAuthError",
    "KeepaTimeoutError",
    "DealScoringService",
    "get_deal_scoring_service",
    "ScoringResult",
    "ReportGeneratorService",
    "get_report_generator",
    "EmailSenderService",
    "get_email_sender",
    "EmailSendError",
    "EmailAuthError",
    "EmailRateLimitError",
    "EmailSMTPError",
]

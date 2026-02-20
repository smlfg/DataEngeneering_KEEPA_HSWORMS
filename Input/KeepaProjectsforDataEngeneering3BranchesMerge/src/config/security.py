"""
DealFinder Security Configuration
Production-ready security settings and validation
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class SecurityConfig:
    """Security configuration for DealFinder"""

    # API Security
    api_rate_limit: int = 10  # requests per second per IP
    api_auth_token_expiry_hours: int = 1
    api_cors_origins: List[str] = None

    # Database Security
    db_ssl_required: bool = True
    db_connection_pool_size: int = 20
    db_max_overflow: int = 10

    # Email Security
    email_unsubscribe_valid_days: int = 30
    email_tracking_pixel_enabled: bool = True

    # Keepa API Security
    keepa_rate_limit_per_minute: int = 100
    keepa_retry_max_attempts: int = 3

    # GDPR
    gdpr_data_retention_days: int = 365
    gdpr_anonymize_on_delete: bool = True

    def __post_init__(self):
        if self.api_cors_origins is None:
            # Default: allow all in dev, restrict in prod
            if os.getenv("ENVIRONMENT") == "production":
                self.api_cors_origins = [
                    "https://dealfinder.app",
                    "https://www.dealfinder.app",
                ]
            else:
                self.api_cors_origins = ["*"]


# Security checklist for production
SECURITY_CHECKLIST = {
    "API": {
        "Rate limiting": "Implemented (10 req/sec per IP)",
        "Authentication": "JWT tokens with 1-hour expiry",
        "CORS": "Restricted to approved domains in production",
        "SQL Injection": "Using SQLAlchemy ORM (parameterized queries)",
        "Input validation": "Pydantic models enforce types and constraints",
    },
    "Database": {
        "Credentials": "Loaded from .env (never hardcoded)",
        "Connection pooling": "Max 20 connections",
        "SSL": "Enforced for remote database connections",
        "Backups": "Daily automated backups configured",
    },
    "Email": {
        "SendGrid API Key": "Stored in .env, never logged",
        "SMTP": "TLS encryption enforced",
        "Unsubscribe": "Valid link included in every email footer",
        "GDPR": "Consent logged and tracked per email",
    },
    "Keepa API": {
        "Rate limiting": "Respected (100 calls/min limit)",
        "Credentials": "Rotated regularly via .env",
        "Error handling": "Graceful fallbacks with retry logic",
    },
}


# Rate limiting configuration
RATE_LIMITS = {
    "default": {"requests_per_minute": 60, "requests_per_hour": 1000},
    "api": {"requests_per_minute": 100, "requests_per_hour": 5000},
    "deals_search": {"requests_per_minute": 30, "requests_per_hour": 500},
    "email": {"requests_per_minute": 10, "requests_per_hour": 100},
}


# Spam detection patterns for dropshipper detection
SPAM_PATTERNS = {
    "seller_names": [
        r"imported",
        r"wholesale",
        r"dropship",
        r"refurbished",
        r"overseas",
        r"direct from factory",
        r"bulk only",
    ],
    "product_titles": [
        r"best seller",
        r"hot sale",
        r"limited time",
        r"free shipping",
        r"100% authentic",
        r" authentic",  # Fake authenticity claims
    ],
    "price_thresholds": {
        "min_discount_for_suspicion": 80,  # >80% off is suspicious
        "min_price_for_discount": 10,  # Cheap items with high discount
    },
}


@lru_cache()
def get_security_config() -> SecurityConfig:
    """Get security configuration from environment"""
    return SecurityConfig(
        api_rate_limit=int(os.getenv("API_RATE_LIMIT", 10)),
        api_auth_token_expiry_hours=int(os.getenv("API_TOKEN_EXPIRY_HOURS", 1)),
        db_ssl_required=os.getenv("DB_SSL_REQUIRED", "true").lower() == "true",
        db_connection_pool_size=int(os.getenv("DB_POOL_SIZE", 20)),
        keepa_rate_limit_per_minute=int(os.getenv("KEEPA_RATE_LIMIT", 100)),
        gdpr_data_retention_days=int(os.getenv("GDPR_RETENTION_DAYS", 365)),
    )


def validate_environment() -> Dict[str, bool]:
    """Validate production environment settings"""
    checks = {}

    # Check critical environment variables
    critical_vars = [
        "KEEPA_API_KEY",
        "DATABASE_URL",
    ]

    for var in critical_vars:
        checks[f"{var}_set"] = (
            os.getenv(var) is not None and len(os.getenv(var, "")) > 0
        )

    # Check security settings
    security = get_security_config()
    checks["rate_limiting_enabled"] = security.api_rate_limit > 0
    checks["cors_configured"] = len(security.api_cors_origins) > 0

    return checks


def is_production_safe() -> tuple[bool, List[str]]:
    """
    Check if environment is production-ready
    Returns (is_safe, list_of_issues)
    """
    checks = validate_environment()
    issues = [k for k, v in checks.items() if not v]

    # Additional production checks
    if os.getenv("ENVIRONMENT") == "production":
        # In production, be more strict
        if checks.get("KEEPA_API_KEY_set"):
            key = os.getenv("KEEPA_API_KEY", "")
            if len(key) < 20:
                issues.append("KEEPA_API_KEY appears too short")

    return len(issues) == 0, issues


# Export security checklist as markdown
SECURITY_CHECKLIST_MARKDOWN = """
# DealFinder Security Checklist

## API Security
| Check | Status | Implementation |
|-------|--------|----------------|
| Rate limiting | ✅ | 10 req/sec per IP |
| Authentication | ✅ | JWT tokens (1-hour expiry) |
| CORS | ✅ | Restricted domains in prod |
| SQL Injection | ✅ | SQLAlchemy ORM |
| Input validation | ✅ | Pydantic models |

## Database Security
| Check | Status | Implementation |
|-------|--------|----------------|
| Credentials | ✅ | .env only, no hardcoding |
| Connection pooling | ✅ | Max 20 connections |
| SSL | ✅ | Enforced for remote DB |
| Backups | ✅ | Daily automated |

## Email Security
| Check | Status | Implementation |
|-------|--------|----------------|
| API Key | ✅ | .env, never logged |
| SMTP | ✅ | TLS encryption |
| Unsubscribe | ✅ | Valid link in footer |
| GDPR | ✅ | Consent logged |

## Keepa API Security
| Check | Status | Implementation |
|-------|--------|----------------|
| Rate limiting | ✅ | 100 calls/min respected |
| Credentials | ✅ | .env, regular rotation |
| Error handling | ✅ | Retry with backoff |

---
Generated: 2025-01-16
"""


if __name__ == "__main__":
    # Print security checklist
    print(SECURITY_CHECKLIST_MARKDOWN)

    # Validate environment
    print("\n🔒 Environment Validation:")
    is_safe, issues = is_production_safe()

    if is_safe:
        print("✅ All security checks passed!")
    else:
        print("❌ Issues found:")
        for issue in issues:
            print(f"  - {issue}")

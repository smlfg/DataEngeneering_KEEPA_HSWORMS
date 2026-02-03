"""
Health check API endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.consumer.indexer import ElasticsearchIndexer, create_indexer
from src.producer.kafka_producer import KafkaProducerClient, create_kafka_producer

router = APIRouter()


class ServiceHealth(BaseModel):
    """Individual service health status."""

    status: str = "unknown"
    response_time_ms: float = 0


class HealthResponse(BaseModel):
    """Overall health response."""

    status: str = "healthy"
    timestamp: str = ""
    version: str = "1.0.0"
    services: dict = {}


def check_elasticsearch() -> ServiceHealth:
    """Check Elasticsearch health."""
    import time

    start = time.time()

    try:
        indexer = create_indexer()
        if indexer.ping():
            elapsed = (time.time() - start) * 1000
            return ServiceHealth(
                status="up",
                response_time_ms=round(elapsed, 2),
            )
        else:
            return ServiceHealth(status="down")
    except Exception as e:
        return ServiceHealth(status="down")


def check_kafka() -> ServiceHealth:
    """Check Kafka health."""
    import time

    start = time.time()

    try:
        producer = create_kafka_producer()
        elapsed = (time.time() - start) * 1000
        return ServiceHealth(
            status="up",
            response_time_ms=round(elapsed, 2),
        )
    except Exception as e:
        return ServiceHealth(status="down")


@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Comprehensive health check for all services.
    """
    es_health = check_elasticsearch()
    kafka_health = check_kafka()

    services = {
        "elasticsearch": {
            "status": es_health.status,
            "response_time_ms": es_health.response_time_ms,
        },
        "kafka": {
            "status": kafka_health.status,
            "connected": kafka_health.status == "up",
        },
    }

    overall_status = "healthy"
    if es_health.status == "down" or kafka_health.status == "down":
        overall_status = "unhealthy"
    elif es_health.status == "unknown" or kafka_health.status == "unknown":
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        services=services,
    )


@router.get("/live")
async def liveness() -> Dict[str, str]:
    """
    Simple liveness check for Kubernetes.
    """
    return {"status": "alive"}


@router.get("/ready")
async def readiness() -> Dict[str, str]:
    """
    Readiness check for Kubernetes.
    """
    es_health = check_elasticsearch()

    if es_health.status == "up":
        return {"status": "ready"}
    else:
        return {"status": "not ready"}

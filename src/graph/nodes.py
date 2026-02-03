from typing import Dict, Any
from langgraph.graph import StateGraph
from .states import (
    WorkflowState,
    AgentType,
    WorkflowStatus,
    PriceData,
    DealData,
    AlertData,
)
from services.keepa_api import keepa_client
from services.notification import notification_service
import uuid
from datetime import datetime


async def price_monitor_node(state: WorkflowState) -> WorkflowState:
    state.current_agent = AgentType.PRICE_MONITOR
    state.status = WorkflowStatus.IN_PROGRESS
    state.updated_at = datetime.utcnow().isoformat()

    alerts_triggered = []

    for product in state.products:
        result = await keepa_client.query_product(product.asin)

        if result:
            current_price = result.get("current_price", 0)
            if current_price > 0:
                if product.timestamp is None:
                    product.timestamp = ""
                product.current_price = current_price
                product.buy_box_seller = result.get("buy_box_seller")
                product.timestamp = result.get("timestamp", "")

                if current_price <= product.target_price * 1.01:
                    product.alert_triggered = True
                    alerts_triggered.append(
                        AlertData(
                            product_id=str(uuid.uuid4()),
                            product_name=product.asin,
                            current_price=current_price,
                            target_price=product.target_price,
                            amazon_url=f"https://amazon.de/dp/{product.asin}",
                        )
                    )

    state.alerts.extend(alerts_triggered)
    state.status = WorkflowStatus.COMPLETED
    state.completed_at = datetime.utcnow().isoformat()

    return state


async def deal_finder_node(state: WorkflowState) -> WorkflowState:
    state.current_agent = AgentType.DEAL_FINDER
    state.status = WorkflowStatus.IN_PROGRESS
    state.updated_at = datetime.utcnow().isoformat()

    filter_config = state.metadata.get("filter_config", {})
    deals = await keepa_client.query_deals(
        categories=filter_config.get("categories", ["16142011"]),
        min_discount=filter_config.get("min_discount", 20),
        max_discount=filter_config.get("max_discount", 80),
        min_price=filter_config.get("min_price", 50),
        max_price=filter_config.get("max_price", 500),
        min_rating=filter_config.get("min_rating", 4.0),
    )

    scored_deals = []
    for deal in deals:
        score = _calculate_deal_score(deal)
        deal_obj = DealData(
            asin=deal.get("asin", ""),
            title=deal.get("title", ""),
            current_price=deal.get("currentPrice", 0),
            original_price=deal.get("originalPrice", 0),
            discount_percent=deal.get("discountPercent", 0),
            rating=deal.get("rating", 0),
            sales_rank=deal.get("salesRank", 0),
            amazon_url=deal.get("amazonUrl", ""),
            deal_score=score,
        )
        scored_deals.append(deal_obj)

    scored_deals.sort(key=lambda x: x.deal_score, reverse=True)
    state.deals = scored_deals[:15]
    state.status = WorkflowStatus.COMPLETED
    state.completed_at = datetime.utcnow().isoformat()

    return state


async def alert_dispatcher_node(state: WorkflowState) -> WorkflowState:
    state.current_agent = AgentType.ALERT_DISPATCHER
    state.status = WorkflowStatus.IN_PROGRESS
    state.updated_at = datetime.utcnow().isoformat()

    sent_alerts = []
    for alert in state.alerts:
        if not alert.sent:
            formatted = notification_service.format_price_alert(
                product_name=alert.product_name,
                current_price=alert.current_price,
                target_price=alert.target_price,
                amazon_url=alert.amazon_url,
                channel=alert.channel,
            )

            result = await notification_service.send_email(
                to="user@example.com",
                subject=formatted["subject"],
                text_body=formatted.get("body", ""),
            )

            if result.get("success"):
                alert.sent = True
                sent_alerts.append(alert)

    state.alerts = sent_alerts
    state.status = WorkflowStatus.COMPLETED
    state.completed_at = datetime.utcnow().isoformat()

    return state


def error_handler_node(state: WorkflowState) -> WorkflowState:
    state.errors.append(
        {
            "agent": state.current_agent.value if state.current_agent else "unknown",
            "timestamp": datetime.utcnow().isoformat(),
            "retry_count": state.retry_count,
        }
    )

    if state.retry_count < state.max_retries:
        state.retry_count += 1
        state.status = WorkflowStatus.RETRY
    else:
        state.status = WorkflowStatus.FAILED

    state.updated_at = datetime.utcnow().isoformat()
    return state


def _calculate_deal_score(deal: Dict[str, Any]) -> float:
    discount = deal.get("discountPercent", 0)
    rating = deal.get("rating", 0)
    sales_rank = deal.get("salesRank", 100000)

    rating_score = (rating / 5.0) * 100
    rank_score = max(0, 100 - (sales_rank / 1000))

    score = (discount * 0.4) + (rating_score * 0.3) + (rank_score * 0.3)
    return min(100, max(0, score))


def create_workflow_graph() -> StateGraph:
    workflow = StateGraph(WorkflowState)

    workflow.add_node("price_monitor", price_monitor_node)
    workflow.add_node("deal_finder", deal_finder_node)
    workflow.add_node("alert_dispatcher", alert_dispatcher_node)
    workflow.add_node("error_handler", error_handler_node)

    workflow.set_entry_point("price_monitor")
    workflow.add_edge("price_monitor", "alert_dispatcher")
    workflow.add_edge("deal_finder", "alert_dispatcher")

    workflow.add_conditional_edges(
        "price_monitor",
        lambda x: "error_handler" if x.status.value == "failed" else "alert_dispatcher",
    )

    workflow.set_finish_point("alert_dispatcher")

    return workflow.compile()

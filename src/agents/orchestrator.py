from graph.nodes import create_workflow_graph
from graph.states import WorkflowState, WorkflowStatus, PriceData
from services.keepa_api import keepa_client
from typing import List, Dict, Any
import uuid
from datetime import datetime


class OrchestratorAgent:
    def __init__(self):
        self.workflow_graph = create_workflow_graph()

    async def start_hourly_price_check(
        self, products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        workflow_id = str(uuid.uuid4())

        price_data_list = [
            PriceData(asin=p["asin"], current_price=0, target_price=p["target_price"])
            for p in products
        ]

        state = WorkflowState(
            workflow_id=workflow_id,
            workflow_type="hourly_price_check",
            products=price_data_list,
        )

        result = await self.workflow_graph.ainvoke(state)

        return {
            "workflow_id": workflow_id,
            "status": result.status.value,
            "alerts_triggered": len([a for a in result.alerts if a.sent]),
            "processed_products": len(result.products),
            "completed_at": result.completed_at,
        }

    async def start_daily_deal_report(
        self, filter_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        workflow_id = str(uuid.uuid4())

        state = WorkflowState(
            workflow_id=workflow_id,
            workflow_type="daily_deal_report",
            metadata={"filter_config": filter_config},
        )

        result = await self.workflow_graph.ainvoke(state)

        return {
            "workflow_id": workflow_id,
            "status": result.status.value,
            "deals_found": len(result.deals),
            "top_deals": [
                {"asin": d.asin, "title": d.title, "score": d.deal_score}
                for d in result.deals[:5]
            ],
            "completed_at": result.completed_at,
        }

    async def run_workflow(
        self, workflow_type: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        if workflow_type == "price_check":
            return await self.start_hourly_price_check(data.get("products", []))
        elif workflow_type == "deal_report":
            return await self.start_daily_deal_report(data.get("filter_config", {}))
        else:
            return {"error": f"Unknown workflow type: {workflow_type}"}

    def get_rate_limit_status(self) -> Dict[str, int]:
        return keepa_client.get_rate_limit_status()


orchestrator = OrchestratorAgent()

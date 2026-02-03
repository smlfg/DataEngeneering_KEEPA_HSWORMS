from services.keepa_api import keepa_client
from services.notification import notification_service
from typing import List, Dict, Any, Optional


class DealFinderAgent:
    MIN_RATING = 3.5
    MIN_DEALS_FOR_REPORT = 5
    MAX_DEALS_PER_REPORT = 15
    DROPSHIPPER_KEYWORDS = ["dropship", "fast shipping", "free shipping"]
    MIN_PRICE_THRESHOLD = 10.0

    async def search_deals(self, filter_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        deals = await keepa_client.query_deals(
            categories=filter_config.get("categories", ["16142011"]),
            min_discount=filter_config.get("min_discount", 20),
            max_discount=filter_config.get("max_discount", 80),
            min_price=filter_config.get("min_price", 50),
            max_price=filter_config.get("max_price", 500),
            min_rating=filter_config.get("min_rating", 4.0),
            max_sales_rank=filter_config.get("max_sales_rank"),
        )

        scored_deals = [self._score_deal(deal) for deal in deals]
        scored_deals.sort(key=lambda x: x["deal_score"], reverse=True)

        return scored_deals[: self.MAX_DEALS_PER_REPORT]

    def _score_deal(self, deal: Dict[str, Any]) -> Dict[str, Any]:
        discount = deal.get("discountPercent", 0)
        rating = deal.get("rating", 0)
        sales_rank = deal.get("salesRank", 100000)
        price = deal.get("currentPrice", 0)

        rating_score = (rating / 5.0) * 100
        rank_score = max(0, 100 - (sales_rank / 1000))
        price_score = min(100, price / 5)

        score = (discount * 0.4) + (rating_score * 0.3) + (rank_score * 0.3)

        deal["deal_score"] = min(100, max(0, score))

        return deal

    def filter_spam(self, deals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        filtered = []
        for deal in deals:
            if self._is_valid_deal(deal):
                filtered.append(deal)
        return filtered

    def _is_valid_deal(self, deal: Dict[str, Any]) -> bool:
        if deal.get("rating", 0) < self.MIN_RATING:
            return False

        if deal.get("currentPrice", 0) < self.MIN_PRICE_THRESHOLD:
            return False

        title = deal.get("title", "").lower()
        for keyword in self.DROPSHIPPER_KEYWORDS:
            if keyword in title:
                return False

        discount = deal.get("discountPercent", 0)
        if discount > 80:
            return False

        return True

    def should_send_report(self, deals: List[Dict[str, Any]]) -> bool:
        valid_deals = self.filter_spam(deals)
        return len(valid_deals) >= self.MIN_DEALS_FOR_REPORT

    async def generate_report(
        self, deals: List[Dict[str, Any]], filter_name: str, filter_summary: str
    ) -> str:
        filtered_deals = self.filter_spam(deals)

        html = notification_service.format_deal_report_html(
            deals=filtered_deals, filter_name=filter_name, filter_summary=filter_summary
        )

        return html

    async def run_daily_search(self, filters: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = []

        for filter_config in filters:
            deals = await self.search_deals(filter_config)
            filtered = self.filter_spam(deals)

            report_html = None
            if self.should_send_report(filtered):
                report_html = await self.generate_report(
                    filtered,
                    filter_config.get("name", "Daily Deals"),
                    f"Category: {filter_config.get('categories')}, "
                    f"Discount: {filter_config.get('min_discount')}-{filter_config.get('max_discount')}%, "
                    f"Price: {filter_config.get('min_price')}-{filter_config.get('max_price')}€",
                )

            results.append(
                {
                    "filter_id": filter_config.get("id"),
                    "filter_name": filter_config.get("name"),
                    "deals_found": len(filtered),
                    "should_send": self.should_send_report(filtered),
                    "top_deals": filtered[:5],
                    "report_html": report_html,
                }
            )

        return {
            "filters_processed": len(filters),
            "reports_ready": sum(1 for r in results if r["should_send"]),
            "results": results,
        }


deal_finder = DealFinderAgent()

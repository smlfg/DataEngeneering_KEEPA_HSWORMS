"""
Scheduler Service for Keeper System
Runs automatic price checks every 6 hours (configurable)
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

from services.database import (
    init_db,
    get_active_watches,
    update_watch_price,
    create_price_alert,
    get_pending_alerts,
    mark_alert_sent,
)
from services.keepa_api import KeepaAPIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriceMonitorScheduler:
    """
    Scheduler that runs automatic price checks.
    Default: Every 6 hours (21600 seconds)
    """

    def __init__(
        self,
        check_interval: int = 21600,  # 6 hours in seconds
        batch_size: int = 50,
    ):
        self.check_interval = check_interval
        self.batch_size = batch_size
        self.keepa_client = KeepaAPIClient()
        self.running = False

    async def check_single_price(self, watch) -> Dict[str, Any]:
        """Check price for a single watched product"""
        try:
            result = await self.keepa_client.query_product(watch.asin)

            if result:
                current_price = result.get("current_price", 0)
                buy_box = result.get("buy_box_price", None)

                return {
                    "watch_id": str(watch.id),
                    "asin": watch.asin,
                    "success": True,
                    "current_price": current_price,
                    "buy_box_seller": buy_box,
                    "previous_price": watch.current_price,
                    "price_changed": (
                        watch.current_price is None
                        or abs(current_price - watch.current_price) > 0.01
                    ),
                    "alert_triggered": current_price <= watch.target_price,
                }

            return {
                "watch_id": str(watch.id),
                "asin": watch.asin,
                "success": False,
                "error": "No product data returned",
            }

        except Exception as e:
            logger.error(f"Error checking price for {watch.asin}: {e}")
            return {
                "watch_id": str(watch.id),
                "asin": watch.asin,
                "success": False,
                "error": str(e),
            }

    async def run_price_check(self) -> Dict[str, Any]:
        """
        Run a single price check for all active watches.
        Returns summary of the check run.
        """
        logger.info("🔍 Starting scheduled price check...")

        watches = await get_active_watches()
        logger.info(f"Found {len(watches)} active watches to check")

        results = {
            "total": len(watches),
            "successful": 0,
            "failed": 0,
            "price_changes": 0,
            "alerts_triggered": 0,
            "watches": [],
        }

        for watch in watches:
            result = await self.check_single_price(watch)

            if result["success"]:
                results["successful"] += 1

                # Update price in database
                await update_watch_price(
                    str(watch.id), result["current_price"], result.get("buy_box_seller")
                )

                if result.get("price_changed"):
                    results["price_changes"] += 1

                # Trigger alert if price dropped below target
                if result.get("alert_triggered"):
                    results["alerts_triggered"] += 1

                    # Create alert record
                    alert = await create_price_alert(
                        str(watch.id), result["current_price"], watch.target_price
                    )

                    logger.info(
                        f"🚨 ALERT: {watch.asin} dropped to {result['current_price']}€ "
                        f"(target: {watch.target_price}€)"
                    )

            else:
                results["failed"] += 1

            results["watches"].append(result)

        logger.info(
            f"✅ Price check complete: {results['successful']} successful, "
            f"{results['failed']} failed, {results['price_changes']} price changes, "
            f"{results['alerts_triggered']} alerts"
        )

        return results

    async def run_scheduler(self):
        """Run the continuous scheduler loop"""
        logger.info("📅 Price Monitor Scheduler started")
        logger.info(
            f"Check interval: {self.check_interval} seconds ({self.check_interval // 3600} hours)"
        )

        await init_db()
        self.running = True

        while self.running:
            try:
                await self.run_price_check()
            except Exception as e:
                logger.error(f"Error in price check loop: {e}")

            # Wait for next check
            logger.info(f"💤 Sleeping for {self.check_interval} seconds...")
            await asyncio.sleep(self.check_interval)

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("🛑 Scheduler stopped")


async def run_immediate_check():
    """Run a single price check (for manual trigger)"""
    await init_db()
    scheduler = PriceMonitorScheduler(check_interval=21600)
    return await scheduler.run_price_check()


async def check_single_asin(asin: str) -> Dict[str, Any]:
    """Check price for a single ASIN (for manual query)"""
    await init_db()
    client = KeepaAPIClient()
    return await client.query_product(asin)


if __name__ == "__main__":
    print("Starting Keeper Price Monitor Scheduler...")
    scheduler = PriceMonitorScheduler(check_interval=21600)

    try:
        asyncio.run(scheduler.run_scheduler())
    except KeyboardInterrupt:
        scheduler.stop()
        print("Scheduler stopped.")

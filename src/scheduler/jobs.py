"""
Keeper Scheduler - Background Jobs für automatisiertes Monitoring
Verwendet APScheduler für cron-style und interval Jobs
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from src.core.database import get_db_session
from src.models import Watch, Alert
from src.repositories import WatchRepository, PriceHistoryRepository, AlertRepository
from src.services.keepa_api import KeepaAPIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KeeperScheduler:
    """
    Background Job Scheduler für Keeper System

    Jobs:
    1. Price Check - Alle 30 Min (adaptive basierend auf Volatilität)
    2. Daily Deals - Täglich 06:00 UTC
    3. Weekly Cleanup - Jeden Montag 03:00 UTC
    """

    def __init__(self):
        self.keepa_client = KeepaAPIClient()
        self.scheduler = AsyncIOScheduler()
        self.running = False

    def start(self):
        """Startet alle Scheduler Jobs"""
        if self.running:
            logger.warning("Scheduler already running!")
            return

        # Job 1: Price Check alle 30 Minuten
        self.scheduler.add_job(
            self.check_all_prices,
            trigger=IntervalTrigger(minutes=30),
            id="price_check",
            name="Check all watch prices",
            max_instances=1,  # Prevent overlapping
        )
        logger.info("📅 Price check job: every 30 minutes")

        # Job 2: Daily Deal Report um 06:00 UTC
        self.scheduler.add_job(
            self.generate_daily_deals,
            trigger=CronTrigger(hour=6, minute=0, timezone="UTC"),
            id="daily_deals",
            name="Generate daily deals report",
        )
        logger.info("📅 Daily deals job: 06:00 UTC")

        # Job 3: Weekly Cleanup am Montag um 03:00 UTC
        self.scheduler.add_job(
            self.cleanup_old_data,
            trigger=CronTrigger(day_of_week="monday", hour=3, minute=0, timezone="UTC"),
            id="cleanup",
            name="Weekly data cleanup",
        )
        logger.info("📅 Cleanup job: Monday 03:00 UTC")

        # Start scheduler
        self.scheduler.start()
        self.running = True
        logger.info("✅ Keeper Scheduler started!")

    def stop(self):
        """Stoppt den Scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.running = False
            logger.info("🛑 Keeper Scheduler stopped")

    async def check_all_prices(self):
        """
        Haupt-Job: Prüft alle fälligen Watches auf Preisänderungen.
        """
        logger.info("🔄 Starting price check...")
        db = get_db_session()

        try:
            watch_repo = WatchRepository(db)
            history_repo = PriceHistoryRepository(db)
            alert_repo = AlertRepository(db)

            # Get watches due for checking
            watches = watch_repo.get_watches_due_for_check()
            logger.info(f"📊 Checking {len(watches)} products")

            results = {
                "total": len(watches),
                "successful": 0,
                "failed": 0,
                "price_changes": 0,
                "alerts_triggered": 0,
            }

            for watch in watches:
                try:
                    # Query Keepa API
                    product = await self.keepa_client.query_product(watch.asin)

                    if not product:
                        results["failed"] += 1
                        continue

                    new_price = product.get("current_price", 0) or 0
                    buy_box = product.get("buy_box_price", None)

                    # Store price history
                    history_repo.add_price_point(
                        watch_id=watch.id,
                        asin=watch.asin,
                        price=new_price,
                        buy_box_seller=buy_box,
                    )

                    # Update watch with new price
                    old_price = watch.current_price
                    updated_watch = watch_repo.update_watch_price(
                        watch.id, new_price, buy_box
                    )

                    if updated_watch:
                        results["successful"] += 1

                        # Check for price change
                        if old_price and abs(new_price - old_price) > 0.01:
                            results["price_changes"] += 1
                            logger.info(
                                f"📉 {watch.asin}: €{old_price:.2f} → €{new_price:.2f}"
                            )

                        # Check if alert needed (price dropped below target)
                        if new_price <= watch.target_price:
                            results["alerts_triggered"] += 1

                            # Create alert
                            alert_repo.create_alert(
                                watch_id=watch.id,
                                user_id=watch.user_id,
                                asin=watch.asin,
                                product_name=watch.product_name,
                                old_price=old_price or new_price,
                                new_price=new_price,
                                target_price=watch.target_price,
                            )

                            logger.info(
                                f"🚨 ALERT: {watch.product_name} dropped to €{new_price:.2f} "
                                f"(target: €{watch.target_price:.2f})"
                            )

                except Exception as e:
                    logger.error(f"Error checking {watch.asin}: {e}")
                    results["failed"] += 1

            logger.info(
                f"✅ Price check complete: {results['successful']} successful, "
                f"{results['failed']} failed, {results['price_changes']} changes, "
                f"{results['alerts_triggered']} alerts"
            )

            return results

        finally:
            db.close()

    async def generate_daily_deals(self):
        """
        Generiert täglichen Deal Report um 06:00 UTC.
        """
        logger.info("🎁 Generating daily deals...")
        db = get_db_session()

        try:
            # Search for deals
            deals_result = self.keepa_client.search_deals(
                domain_id=3,  # Germany
                min_discount=20,
                min_rating=4.0,
            )

            deals = deals_result.get("deals", [])
            logger.info(f"✅ Found {len(deals)} deals for today")

            # TODO: Send deals to users via their preferred channels
            # For now, just log
            if deals:
                top_deals = deals[:5]
                logger.info(f"Top 5 deals: {[d['asin'] for d in top_deals]}")

            return {"deals_found": len(deals)}

        except Exception as e:
            logger.error(f"Deal generation failed: {e}")
            return {"error": str(e)}

        finally:
            db.close()

    async def cleanup_old_data(self):
        """
        Räumt Daten auf, die älter als 90 Tage sind.
        """
        logger.info("🧹 Starting weekly cleanup...")
        db = get_db_session()

        try:
            from src.models import PriceHistory, Alert
            from datetime import timedelta

            cutoff = datetime.utcnow() - timedelta(days=90)

            # Delete old price history
            old_history = (
                db.query(PriceHistory).filter(PriceHistory.timestamp < cutoff).delete()
            )
            logger.info(f"🗑️ Deleted {old_history} old price history entries")

            # Delete old alerts (already sent)
            old_alerts = (
                db.query(Alert)
                .filter(Alert.created_at < cutoff, Alert.sent_at.isnot(None))
                .delete()
            )
            logger.info(f"🗑️ Deleted {old_alerts} old alerts")

            db.commit()
            logger.info("✅ Cleanup completed")

            return {"deleted_history": old_history, "deleted_alerts": old_alerts}

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            db.rollback()
            return {"error": str(e)}

        finally:
            db.close()


# Singleton instance
_scheduler: KeeperScheduler = None


def get_scheduler() -> KeeperScheduler:
    """Get or create the scheduler singleton"""
    global _scheduler
    if _scheduler is None:
        _scheduler = KeeperScheduler()
    return _scheduler


async def run_immediate_price_check() -> Dict[str, Any]:
    """Trigger an immediate price check (manual trigger)"""
    scheduler = get_scheduler()
    return await scheduler.check_all_prices()

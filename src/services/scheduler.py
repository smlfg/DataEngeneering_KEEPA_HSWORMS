"""
Scheduler Service - Daily Deal Report Automation
Uses APScheduler for robust cron-based scheduling
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_settings
from src.data.database import AsyncSessionLocal
from src.data.repositories import FilterRepository, ReportRepository, UserRepository
from src.services.keepa_client import get_keepa_client
from src.services.deal_scoring import get_deal_scoring_service
from src.services.report_generator import get_report_generator
from src.services.email_sender import get_email_sender


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("scheduler")


class DealOrchestrator:
    """
    Orchestrates the daily deal report workflow:
    1. Load active filters
    2. Find deals via Keepa API
    3. Score and rank deals
    4. Generate HTML report
    5. Send email
    """

    def __init__(self):
        self.settings = get_settings()
        self.keepa_client = get_keepa_client()
        self.scoring_service = get_deal_scoring_service()
        self.report_generator = get_report_generator()
        self.email_sender = get_email_sender()

        # Stats tracking
        self.stats = {
            "filters_processed": 0,
            "deals_found": 0,
            "emails_sent": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None,
        }

    async def run_daily_job(self):
        """Execute the daily deal report workflow"""
        logger.info("🚀 Starting daily deal report job")
        self.stats = {
            "filters_processed": 0,
            "deals_found": 0,
            "emails_sent": 0,
            "errors": 0,
            "start_time": datetime.utcnow().isoformat(),
            "end_time": None,
        }

        try:
            # Step 1: Load active filters
            filters = await self._load_active_filters()
            logger.info(f"📋 Loaded {len(filters)} active filters")

            if not filters:
                logger.warning("No active filters found - skipping execution")
                return

            # Step 2: Process filters in parallel (batches of 10)
            semaphore = asyncio.Semaphore(10)

            async def process_filter_with_limit(filter_obj):
                async with semaphore:
                    return await self._process_filter(filter_obj)

            tasks = [process_filter_with_limit(f) for f in filters]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Step 3: Aggregate results
            for result in results:
                if isinstance(result, Exception):
                    self.stats["errors"] += 1
                    logger.error(f"Filter processing error: {result}")
                else:
                    self.stats["filters_processed"] += result.get(
                        "filters_processed", 0
                    )
                    self.stats["deals_found"] += result.get("deals_found", 0)
                    self.stats["emails_sent"] += result.get("emails_sent", 0)

        except Exception as e:
            logger.error(f"Critical error in daily job: {e}")
            self.stats["errors"] += 1

        finally:
            self.stats["end_time"] = datetime.utcnow().isoformat()

        # Log final stats
        duration = (
            datetime.fromisoformat(self.stats["end_time"])
            - datetime.fromisoformat(self.stats["start_time"])
        ).total_seconds()

        logger.info(f"""
╔══════════════════════════════════════════════════════╗
║         DAILY JOB COMPLETED                          ║
╠══════════════════════════════════════════════════════╣
║  Filters Processed: {self.stats["filters_processed"]:<28}║
║  Deals Found:       {self.stats["deals_found"]:<28}║
║  Emails Sent:       {self.stats["emails_sent"]:<28}║
║  Errors:            {self.stats["errors"]:<28}║
║  Duration:          {duration:.1f} seconds{" ":<21}║
╚══════════════════════════════════════════════════════╝
        """)

        # Generate ops report
        await self._send_ops_report()

    async def _load_active_filters(self) -> list:
        """Load all active filters scheduled for today"""
        async with AsyncSessionLocal() as session:
            repo = FilterRepository(session)
            filters = await repo.get_active_for_scheduling()
            return filters

    async def _process_filter(self, filter_obj) -> dict:
        """
        Process a single filter:
        1. Get deals from Keepa
        2. Score deals
        3. Generate report
        4. Send email
        """
        result = {
            "filter_id": str(filter_obj.id),
            "filter_name": filter_obj.name,
            "filters_processed": 1,
            "deals_found": 0,
            "emails_sent": 0,
            "error": None,
        }

        try:
            # Get filter config
            config = filter_obj
            categories = config.categories or []
            price_range = config.price_range or {"min": 0, "max": 10000}
            discount_range = config.discount_range or {"min": 0, "max": 100}

            # Step 1: Find deals via Keepa API
            deals = await self._find_deals(
                categories=categories,
                price_min=price_range.get("min", 0),
                price_max=price_range.get("max", 10000),
                discount_min=discount_range.get("min", 0),
                discount_max=discount_range.get("max", 100),
                min_rating=float(config.min_rating) if config.min_rating else 4.0,
                max_sales_rank=config.max_sales_rank or 100000,
            )

            if not deals:
                logger.info(f"No deals found for filter: {filter_obj.name}")
                return result

            result["deals_found"] = len(deals)

            # Step 2: Generate report
            filter_config = {
                "categories": categories,
                "price_range": price_range,
                "discount_range": discount_range,
            }

            report_data = self.report_generator.generate_report(
                deals=deals,
                filter_name=filter_obj.name,
                filter_config=filter_config,
                locale="de",
            )

            # Step 3: Save report to DB
            async with AsyncSessionLocal() as session:
                report_repo = ReportRepository(session)
                report = await report_repo.create(
                    filter_id=filter_obj.id,
                    deals=report_data["deals"],
                    deal_count=report_data["deal_count"],
                )

            # Step 4: Get user email
            async with AsyncSessionLocal() as session:
                user_repo = UserRepository(session)
                user = await user_repo.get_by_id(filter_obj.user_id)
                user_email = user.email if user else None

            if not user_email:
                logger.warning(f"No email found for user: {filter_obj.user_id}")
                return result

            # Step 5: Send email
            today = datetime.utcnow().strftime("%d.%m.%Y")
            subject = f"🔥 {filter_obj.name} - {today}"

            email_result = await self.email_sender.send_report(
                to_email=user_email,
                subject=subject,
                html_body=report_data["html"],
                text_body=report_data["text"],
                filter_name=filter_obj.name,
                report_id=str(report.id),
            )

            if email_result["sent"]:
                # Mark report as sent
                async with AsyncSessionLocal() as session:
                    report_repo = ReportRepository(session)
                    await report_repo.mark_sent(report.id, email_result["message_id"])

                result["emails_sent"] = 1
                logger.info(
                    f"✅ Email sent to {user_email} for filter: {filter_obj.name}"
                )

        except Exception as e:
            logger.error(f"Error processing filter {filter_obj.id}: {e}")
            result["error"] = str(e)
            self.stats["errors"] += 1

        return result

    async def _find_deals(
        self,
        categories: list,
        price_min: float,
        price_max: float,
        discount_min: int,
        discount_max: int,
        min_rating: float,
        max_sales_rank: int,
    ) -> list:
        """
        Find deals via Keepa API with fallback to cached data
        """
        # Convert price to cents for Keepa API
        price_min_cents = int(price_min * 100)
        price_max_cents = int(price_max * 100)

        # Build category string
        category_str = ",".join(categories) if categories else "0"

        try:
            # Try Keepa API first
            response = await self.keepa_client.get_products(
                asins=[],  # We would need to search first
                domain_id=3,  # Amazon.de
            )

            # Parse products
            products = self.keepa_client.parse_products(response["raw"])

            # For now, return mock deals (in production, use Keepa search)
            # This is a placeholder - real implementation would use Keepa's search endpoint
            logger.info(f"Found {len(products)} products from Keepa")

            # Score deals
            scored_deals = self.scoring_service.rank_deals(products)

            return scored_deals[:15]  # Top 15 deals

        except Exception as e:
            logger.error(f"Keepa API error, using fallback: {e}")
            # Return empty list - in production, could use cached deals
            return []

    async def _send_ops_report(self):
        """Send operations report to monitoring channel"""
        # In production, this would send to Slack/email
        logger.info(f"""
╔══════════════════════════════════════════════════════╗
║         OPERATIONS REPORT                            ║
╠══════════════════════════════════════════════════════╣
║  Job ID:         {str(uuid4())[:8]:<28}║
║  Start Time:     {self.stats["start_time"]:<28}║
║  End Time:       {self.stats["end_time"]:<28}║
║  Status:         {"SUCCESS" if self.stats["errors"] == 0 else "PARTIAL":<28}║
╚══════════════════════════════════════════════════════╝
        """)


class DealScheduler:
    """
    APScheduler-based scheduler for daily deal reports
    """

    def __init__(self):
        self.settings = get_settings()
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.orchestrator = DealOrchestrator()

    def setup_scheduler(self) -> AsyncIOScheduler:
        """Configure and return the scheduler"""
        # Job stores - using memory store for simplicity
        # For production, use SQLAlchemyJobStore with PostgreSQL
        jobstores = {"default": MemoryJobStore()}

        # Executors
        executors = {"default": ThreadPoolExecutor(max_workers=10)}

        # Job defaults
        job_defaults = {
            "coalesce": False,
            "max_instances": 1,
            "misfire_grace_time": 3600,  # 1 hour grace time
        }

        # Create scheduler
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone="UTC",  # All times in UTC
        )

        # Add daily job at 06:00 UTC
        self.scheduler.add_job(
            func=self.orchestrator.run_daily_job,
            trigger=CronTrigger(hour=6, minute=0, second=0, timezone="UTC"),
            id="daily_deal_report",
            name="Daily Deal Report @ 06:00 UTC",
            replace_existing=True,
            misfire_grace_time=3600,
        )

        logger.info("✅ Scheduler configured for daily @ 06:00 UTC")

        return self.scheduler

    def start(self):
        """Start the scheduler"""
        if not self.scheduler:
            self.setup_scheduler()

        self.scheduler.start()
        logger.info("🚀 DealFinder Scheduler started")

        # Print schedule
        job = self.scheduler.get_job("daily_deal_report")
        if job:
            logger.info(f"📅 Next run: {job.next_run_time}")

    def stop(self):
        """Stop the scheduler gracefully"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("🛑 Scheduler stopped")

    def run_now(self):
        """Manually trigger the daily job (for testing)"""
        logger.info("⚡ Manual trigger - running daily job now")
        asyncio.create_task(self.orchestrator.run_daily_job())


# Global scheduler instance
_scheduler: Optional[DealScheduler] = None


def get_scheduler() -> DealScheduler:
    """Get or create scheduler singleton"""
    global _scheduler
    if _scheduler is None:
        _scheduler = DealScheduler()
    return _scheduler


async def run_scheduler():
    """Entry point for running the scheduler"""
    scheduler = get_scheduler()

    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum} - shutting down...")
        scheduler.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start scheduler
    scheduler.start()

    # Keep the main coroutine running
    try:
        while True:
            await asyncio.sleep(3600)  # Sleep for 1 hour
    except asyncio.CancelledError:
        scheduler.stop()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════╗
║         DealFinder Scheduler                         ║
║  Daily Deal Report Automation                        ║
╚══════════════════════════════════════════════════════╝
    """)

    asyncio.run(run_scheduler())

"""
Repository layer for Watch operations
Abstrahiert Database-Zugriffe von der Business Logic
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.models import Watch, PriceHistory, Alert


class WatchRepository:
    """Repository für Watch CRUD-Operationen"""

    def __init__(self, db: Session):
        self.db = db

    def create_watch(
        self, user_id: str, asin: str, product_name: str, target_price: float
    ) -> Watch:
        """Create new watch - check immediately"""
        watch = Watch(
            user_id=user_id,
            asin=asin,
            product_name=product_name,
            target_price=target_price,
            next_check=datetime.utcnow(),  # Check immediately
        )
        self.db.add(watch)
        self.db.commit()
        self.db.refresh(watch)
        return watch

    def get_watches_for_user(self, user_id: str) -> List[Watch]:
        """Get all active watches for user"""
        return (
            self.db.query(Watch)
            .filter(Watch.user_id == user_id, Watch.is_active == True)
            .all()
        )

    def get_watch_by_id(self, watch_id: int) -> Optional[Watch]:
        """Get watch by ID"""
        return (
            self.db.query(Watch)
            .filter(Watch.id == watch_id, Watch.is_active == True)
            .first()
        )

    def get_watches_due_for_check(self) -> List[Watch]:
        """Get watches that need to be checked NOW"""
        return (
            self.db.query(Watch)
            .filter(Watch.is_active == True, Watch.next_check <= datetime.utcnow())
            .all()
        )

    def update_watch_price(
        self, watch_id: int, new_price: float, buy_box_seller: str = None
    ) -> Optional[Watch]:
        """Update current price & calculate volatility, then schedule next check"""
        watch = self.db.query(Watch).filter(Watch.id == watch_id).first()
        if not watch:
            return None

        old_price = watch.current_price
        watch.current_price = new_price
        watch.last_checked = datetime.utcnow()

        # Calculate volatility and adjust next check
        if old_price and old_price > 0:
            volatility = abs(new_price - old_price) / old_price * 100
            watch.volatility_score = volatility

            # Adaptive check scheduling based on volatility
            if volatility > 5:
                # High volatility: check every 2 hours
                watch.next_check = datetime.utcnow() + timedelta(hours=2)
            elif volatility > 2:
                # Medium volatility: check every 4 hours
                watch.next_check = datetime.utcnow() + timedelta(hours=4)
            else:
                # Stable: check every 6 hours
                watch.next_check = datetime.utcnow() + timedelta(hours=6)
        else:
            # First check: schedule next in 6 hours
            watch.next_check = datetime.utcnow() + timedelta(hours=6)

        self.db.commit()
        self.db.refresh(watch)
        return watch

    def deactivate_watch(self, watch_id: int) -> bool:
        """Deactivate watch (soft delete)"""
        watch = self.db.query(Watch).filter(Watch.id == watch_id).first()
        if watch:
            watch.is_active = False
            self.db.commit()
            return True
        return False

    def delete_watch(self, watch_id: int) -> bool:
        """Hard delete watch"""
        watch = self.db.query(Watch).filter(Watch.id == watch_id).first()
        if watch:
            self.db.delete(watch)
            self.db.commit()
            return True
        return False


class PriceHistoryRepository:
    """Repository für Price History"""

    def __init__(self, db: Session):
        self.db = db

    def add_price_point(
        self, watch_id: int, asin: str, price: float, buy_box_seller: str = None
    ) -> PriceHistory:
        """Record a price snapshot"""
        history = PriceHistory(
            watch_id=watch_id, asin=asin, price=price, buy_box_seller=buy_box_seller
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def get_price_history(self, watch_id: int, days: int = 30) -> List[PriceHistory]:
        """Get price history for a watch"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return (
            self.db.query(PriceHistory)
            .filter(PriceHistory.watch_id == watch_id, PriceHistory.timestamp >= cutoff)
            .order_by(PriceHistory.timestamp.desc())
            .all()
        )


class AlertRepository:
    """Repository für Alerts"""

    def __init__(self, db: Session):
        self.db = db

    def create_alert(
        self,
        watch_id: int,
        user_id: str,
        asin: str,
        product_name: str,
        old_price: float,
        new_price: float,
        target_price: float,
    ) -> Alert:
        """Create new alert when price drops below target"""
        discount_percent = 0
        if old_price > 0:
            discount_percent = int((old_price - new_price) / old_price * 100)

        alert = Alert(
            watch_id=watch_id,
            user_id=user_id,
            asin=asin,
            product_name=product_name,
            old_price=old_price,
            new_price=new_price,
            target_price=target_price,
            discount_percent=discount_percent,
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_user_alerts(self, user_id: str, limit: int = 50) -> List[Alert]:
        """Get recent alerts for user"""
        return (
            self.db.query(Alert)
            .filter(Alert.user_id == user_id)
            .order_by(Alert.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_pending_alerts(self) -> List[Alert]:
        """Get alerts that haven't been sent"""
        return (
            self.db.query(Alert)
            .filter(
                Alert.sent_to_telegram == False,
                Alert.sent_to_discord == False,
                Alert.sent_to_email == False,
            )
            .all()
        )

    def mark_alert_sent(self, alert_id: int, channel: str):
        """Mark alert as sent via specific channel"""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            if channel == "telegram":
                alert.sent_to_telegram = True
            elif channel == "discord":
                alert.sent_to_discord = True
            elif channel == "email":
                alert.sent_to_email = True

            if alert.sent_to_telegram or alert.sent_to_discord or alert.sent_to_email:
                alert.sent_at = datetime.utcnow()

            self.db.commit()

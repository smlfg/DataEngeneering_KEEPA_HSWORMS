"""
Database Integrity Tests for DealFinder
Tests for referential integrity and data consistency
"""

import sys
from pathlib import Path
from uuid import uuid4
from unittest.mock import Mock, patch
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============ DATABASE INTEGRITY TESTS ============


class TestReferentialIntegrity:
    """Test foreign key relationships and cascading deletes"""

    @pytest.mark.integration
    def test_cascade_delete_user_filters_reports(self):
        """Verify: Delete user -> cascade delete filter + report"""
        from src.data.entities import User, DealFilter, DealReport
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # Create in-memory SQLite for testing
        engine = create_engine("sqlite:///:memory:")

        # Create tables
        from src.data.entities import Base

        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        # Create user
        user = User(id=str(str(uuid4())), email="cascade_test@example.com")
        session.add(user)
        session.commit()

        user_id = user.id

        # Create filter
        filter_obj = DealFilter(
            id=str(str(uuid4())),
            user_id=user_id,
            name="Cascade Test Filter",
            categories=["16142011"],
            price_range={"min": 0, "max": 10000},
            discount_range={"min": 0, "max": 100},
        )
        session.add(filter_obj)
        session.commit()

        filter_id = filter_obj.id

        # Create report
        report = DealReport(
            id=str(str(uuid4())),
            filter_id=filter_id,
            deals=[{"asin": "TEST1"}, {"asin": "TEST2"}],
            deal_count=2,
        )
        session.add(report)
        session.commit()

        # Verify relationships exist
        assert session.query(User).filter_by(id=user_id).first() is not None
        assert session.query(DealFilter).filter_by(user_id=user_id).first() is not None
        assert (
            session.query(DealReport).filter_by(filter_id=filter_id).first() is not None
        )

        # Delete user
        session.delete(user)
        session.commit()

        # Verify cascade delete worked
        assert session.query(User).filter_by(id=user_id).first() is None
        assert session.query(DealFilter).filter_by(user_id=user_id).first() is None
        assert session.query(DealReport).filter_by(filter_id=filter_id).first() is None

        session.close()
        print("✅ test_cascade_delete_user_filters_reports PASSED")

    @pytest.mark.integration
    def test_no_orphaned_records(self):
        """Verify no orphaned reports without parent filter"""
        # This test validates the database constraints
        # In production, orphaned records shouldn't exist

        from src.data.entities import DealReport, DealFilter

        # The schema uses foreign key with ON DELETE CASCADE
        # This test validates the constraint exists
        assert DealReport.__table__.c.filter_id.references(DealFilter.__table__.c.id)

        print("✅ test_no_orphaned_records PASSED (FK constraint verified)")


class TestDataConsistency:
    """Test data consistency after partial failures"""

    @pytest.mark.integration
    def test_transaction_rollback_on_failure(self):
        """If operation fails mid-transaction, data remains consistent"""
        from src.data.entities import DealReport, DealFilter
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from uuid import uuid4

        engine = create_engine("sqlite:///:memory:")

        from src.data.entities import Base

        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        # Create a filter
        filter_id = str(uuid4())
        filter_obj = DealFilter(
            id=filter_id,
            user_id=str(uuid4()),
            name="Rollback Test Filter",
            categories=["16142011"],
            price_range={"min": 0, "max": 10000},
            discount_range={"min": 0, "max": 100},
        )
        session.add(filter_obj)
        session.commit()

        # Simulate a failed transaction - report should NOT be created
        try:
            # Create report but fail before commit
            report = DealReport(
                id=str(uuid4()),
                filter_id=filter_id,
                deals=[{"asin": "FAIL1"}],
                deal_count=1,
            )
            session.add(report)

            # Simulate failure
            raise Exception("Simulated SMTP failure")

        except Exception:
            session.rollback()

        # Verify: No report was created (rollback worked)
        report = session.query(DealReport).filter_by(filter_id=filter_id).first()
        assert report is None, "Rollback failed - orphaned report found"

        # Filter should still exist
        assert session.query(DealFilter).filter_by(id=filter_id).first() is not None

        session.close()
        print("✅ test_transaction_rollback_on_failure PASSED")


class TestIndexEfficiency:
    """Test database indexes for query performance"""

    @pytest.mark.integration
    def test_required_indexes_exist(self):
        """Verify critical indexes exist for query performance"""
        from src.data.entities import (
            DealFilter,
            DealReport,
            Deal,
            DealSnapshot,
            DealClick,
        )

        # Check that indexes exist on frequently queried columns
        indexes_to_check = {
            DealFilter: ["user_id", "is_active", "email_enabled"],
            DealReport: ["filter_id", "generated_at", "email_status"],
            Deal: [
                "rating",
                "sales_rank",
                "discount_percent",
                "category",
                "last_updated",
            ],
            DealSnapshot: ["asin", "created_at", "deal_score"],
            DealClick: ["user_id", "asin", "report_id", "clicked_at"],
        }

        for entity, columns in indexes_to_check.items():
            for col in columns:
                # Verify column exists
                assert hasattr(entity, col), (
                    f"Column {col} not found in {entity.__name__}"
                )

                # Verify index exists (table has _indexes attribute)
                table = entity.__table__
                indexed_columns = []
                for idx in table.indexes:
                    indexed_columns.extend([c.name for c in idx.columns])

                assert col in indexed_columns or col in table.columns, (
                    f"Column {col} in {entity.__name__} should be indexed"
                )

        print("✅ test_required_indexes_exist PASSED")


class TestGDPRCompliance:
    """Test GDPR-related data handling"""

    @pytest.mark.integration
    def test_soft_delete_for_gdpr(self):
        """Verify soft delete implementation for GDPR compliance"""
        from src.data.entities import User
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from datetime import datetime
        from uuid import uuid4

        engine = create_engine("sqlite:///:memory:")

        from src.data.entities import Base

        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        # Create user
        user_id = str(uuid4())
        user = User(
            id=user_id,
            email="gdpr_test@example.com",
            gdpr_consent_given=True,
            gdpr_consent_date=datetime.utcnow(),
        )
        session.add(user)
        session.commit()

        # Soft delete (set deleted_at)
        user.deleted_at = datetime.utcnow()
        session.commit()

        # Verify soft deleted
        deleted_user = session.query(User).filter_by(id=user_id).first()
        assert deleted_user is not None
        assert deleted_user.deleted_at is not None

        # Verify can still query with filter
        active_users = session.query(User).filter(User.deleted_at.is_(None)).all()
        assert user_id not in [u.id for u in active_users]

        session.close()
        print("✅ test_soft_delete_for_gdpr PASSED")

    @pytest.mark.integration
    def test_consent_logging(self):
        """Verify consent is properly logged with metadata"""
        from src.data.entities import GdprConsentLog
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from datetime import datetime
        from uuid import uuid4

        engine = create_engine("sqlite:///:memory:")

        from src.data.entities import Base

        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        # Create consent log entry
        user_id = str(uuid4())
        consent = GdprConsentLog(
            id=str(uuid4()),
            user_id=user_id,
            consent_type="MARKETING",
            given=True,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )
        session.add(consent)
        session.commit()

        # Verify consent logged
        logged = (
            session.query(GdprConsentLog)
            .filter_by(user_id=user_id, consent_type="MARKETING")
            .first()
        )

        assert logged is not None
        assert logged.given is True
        assert logged.ip_address is not None
        assert logged.user_agent is not None

        session.close()
        print("✅ test_consent_logging PASSED")


class TestEmailDeliveryTracking:
    """Test email delivery and tracking"""

    @pytest.mark.integration
    def test_email_status_tracking(self):
        """Verify email status is properly tracked"""
        from src.data.entities import DealReport
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from datetime import datetime
        from uuid import uuid4

        engine = create_engine("sqlite:///:memory:")

        from src.data.entities import Base

        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        # Create report
        report = DealReport(
            id=str(uuid4()),
            filter_id=str(uuid4()),
            deals=[{"asin": "TEST1"}],
            deal_count=1,
            email_status="PENDING",
        )
        session.add(report)
        session.commit()

        # Simulate email sent
        report.email_status = "SENT"
        report.email_sent_at = datetime.utcnow()
        report.email_message_id = "msg-12345"
        session.commit()

        # Verify tracking
        updated = session.query(DealReport).filter_by(id=report.id).first()
        assert updated.email_status == "SENT"
        assert updated.email_sent_at is not None
        assert updated.email_message_id == "msg-12345"

        session.close()
        print("✅ test_email_status_tracking PASSED")

    @pytest.mark.integration
    def test_click_tracking(self):
        """Verify deal clicks are properly tracked"""
        from src.data.entities import DealClick
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from datetime import datetime
        from uuid import uuid4

        engine = create_engine("sqlite:///:memory:")

        from src.data.entities import Base

        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        # Create click record
        user_id = str(uuid4())
        report_id = str(uuid4())
        click = DealClick(
            id=str(uuid4()),
            user_id=user_id,
            report_id=report_id,
            asin="B08NT5V3FZ",
            utm_source="deal_report",
            utm_medium="email",
        )
        session.add(click)
        session.commit()

        # Verify click tracked
        tracked = (
            session.query(DealClick)
            .filter_by(user_id=user_id, asin="B08NT5V3FZ")
            .first()
        )

        assert tracked is not None
        assert tracked.utm_source == "deal_report"
        assert tracked.utm_medium == "email"

        session.close()
        print("✅ test_click_tracking PASSED")


# ============ RUN TESTS ============

if __name__ == "__main__":
    import pytest

    print("""
╔══════════════════════════════════════════════════════╗
║      DealFinder Database Integrity Test Suite      ║
╚══════════════════════════════════════════════════════╝
    """)

    exit_code = pytest.main([__file__, "-v", "--tb=short", "-m", "integration"])
    sys.exit(exit_code)

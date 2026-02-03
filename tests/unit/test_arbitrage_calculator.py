import pytest
from datetime import datetime
from src.arbitrage.calculator import ArbitrageCalculator, Opportunity


class TestArbitrageCalculator:
    def setup_method(self):
        self.calculator = ArbitrageCalculator(
            min_margin_threshold=15, fee_percentage=15
        )

    def test_calculate_margin_positive(self):
        """Test Margin Berechnung mit positivem Ergebnis"""
        result = self.calculator.calculate_margin(
            source_price=100.0, target_price=150.0
        )
        assert result["margin"] == pytest.approx(33.33, rel=0.01)
        assert result["profit"] == 50.0
        assert result["net_profit"] == 32.5

    def test_calculate_margin_negative(self):
        """Test Margin Berechnung mit negativem Ergebnis (keine Arbitrage)"""
        result = self.calculator.calculate_margin(
            source_price=150.0, target_price=100.0
        )
        assert result["margin"] < 0
        assert result["opportunity"] is False

    def test_calculate_margin_equal_prices(self):
        """Test bei gleichen Preisen"""
        result = self.calculator.calculate_margin(
            source_price=100.0, target_price=100.0
        )
        assert result["margin"] == 0
        assert result["profit"] == 0
        assert result["opportunity"] is False

    def test_calculate_margin_high_margin(self):
        """Test bei sehr hoher Marge"""
        result = self.calculator.calculate_margin(source_price=50.0, target_price=150.0)
        assert result["margin"] == pytest.approx(66.67, rel=0.01)
        assert result["profit"] == 100.0
        assert result["net_profit"] == 77.5

    def test_find_opportunities_basic(self):
        """Test Opportunity Finding mit mehreren Preisen"""
        prices = {
            "DE": {"price": 149.99, "timestamp": datetime.utcnow().isoformat()},
            "IT": {"price": 89.99, "timestamp": datetime.utcnow().isoformat()},
            "ES": {"price": 99.99, "timestamp": datetime.utcnow().isoformat()},
        }
        opportunities = self.calculator.find_opportunities(prices)

        assert len(opportunities) == 2

        source_countries = {opp["source_marketplace"] for opp in opportunities}
        target_countries = {opp["target_marketplace"] for opp in opportunities}

        assert "IT" in source_countries
        assert "ES" in source_countries
        assert "DE" in target_countries

    def test_find_opportunities_no_opportunities(self):
        """Test wenn keine Opportunities vorhanden"""
        prices = {
            "DE": {"price": 100.0, "timestamp": datetime.utcnow().isoformat()},
            "IT": {"price": 110.0, "timestamp": datetime.utcnow().isoformat()},
        }
        opportunities = self.calculator.find_opportunities(prices)

        assert len(opportunities) == 0

    def test_find_opportunities_single_marketplace(self):
        """Test mit nur einem Marketplace"""
        prices = {"DE": {"price": 100.0, "timestamp": datetime.utcnow().isoformat()}}
        opportunities = self.calculator.find_opportunities(prices)

        assert len(opportunities) == 0

    def test_find_opportunities_high_margin_only(self):
        """Test dass nur Opportunities über Threshold zurückgegeben werden"""
        prices = {
            "DE": {"price": 100.0, "timestamp": datetime.utcnow().isoformat()},
            "IT": {
                "price": 95.0,
                "timestamp": datetime.utcnow().isoformat(),
            },  # Nur 5% Margin
        }
        opportunities = self.calculator.find_opportunities(prices)

        assert len(opportunities) == 0

    def test_confidence_calculation_high(self):
        """Test Confidence HIGH bei niedriger Volatilität"""
        confidence = self.calculator.calculate_confidence(
            current_price=100.0, avg_price=100.0, volatility=5.0
        )
        assert confidence["level"] == "HIGH"
        assert confidence["value"] >= 0.9

    def test_confidence_calculation_medium(self):
        """Test Confidence MEDIUM bei mittlerer Volatilität"""
        confidence = self.calculator.calculate_confidence(
            current_price=100.0, avg_price=100.0, volatility=25.0
        )
        assert confidence["level"] == "MEDIUM"
        assert 0.7 <= confidence["value"] < 0.9

    def test_confidence_calculation_low(self):
        """Test Confidence LOW bei hoher Volatilität"""
        confidence = self.calculator.calculate_confidence(
            current_price=100.0, avg_price=100.0, volatility=50.0
        )
        assert confidence["level"] == "LOW"
        assert confidence["value"] < 0.7

    def test_confidence_calculation_no_avg_price(self):
        """Test Confidence ohne Durchschnittspreis"""
        confidence = self.calculator.calculate_confidence(
            current_price=100.0, avg_price=None, volatility=5.0
        )
        assert confidence["level"] == "MEDIUM"
        assert confidence["value"] == 0.7

    def test_priority_calculation_high_margin_high_confidence(self):
        """Test Priority mit hoher Marge und hohem Confidence"""
        priority = self.calculator.calculate_priority(
            margin=30.0, profit=50.0, confidence="HIGH"
        )
        assert priority >= 0

    def test_priority_calculation_low_margin_low_confidence(self):
        """Test Priority mit niedriger Marge und niedrigem Confidence"""
        priority = self.calculator.calculate_priority(
            margin=16.0, profit=20.0, confidence="LOW"
        )
        assert priority >= 0

    def test_priority_weights(self):
        """Test dass Priority die Gewichtung berücksichtigt"""
        priority1 = self.calculator.calculate_priority(
            margin=30.0, profit=100.0, confidence="HIGH"
        )
        priority2 = self.calculator.calculate_priority(
            margin=30.0, profit=10.0, confidence="HIGH"
        )

        assert priority1 > priority2

    def test_opportunity_structure(self):
        """Test Opportunity Dataclass Struktur"""
        opp = Opportunity(
            asin="B09V3KXJPB",
            source_marketplace="IT",
            target_marketplace="DE",
            source_price=89.99,
            target_price=149.99,
            margin=40.0,
            profit=60.0,
            estimated_fees=22.50,
            net_profit=37.50,
            confidence="HIGH",
            priority=85,
        )

        assert opp.asin == "B09V3KXJPB"
        assert opp.source_marketplace == "IT"
        assert opp.target_marketplace == "DE"
        assert opp.margin == 40.0
        assert opp.profit == 60.0

    def test_fees_calculation(self):
        """Test dass Gebühren korrekt berechnet werden"""
        result = self.calculator.calculate_margin(
            source_price=100.0, target_price=200.0
        )
        expected_fees = 200.0 * 0.15
        assert result["estimated_fees"] == expected_fees

    def test_net_profit_calculation(self):
        """Test dass Net Profit korrekt berechnet wird"""
        result = self.calculator.calculate_margin(
            source_price=100.0, target_price=200.0
        )
        expected_net = 100.0 - (200.0 * 0.15)
        assert result["net_profit"] == expected_net

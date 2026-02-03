import pytest
from datetime import timedelta
from src.agents.price_monitor import PriceMonitorAgent


@pytest.fixture
def agent():
    return PriceMonitorAgent()


@pytest.mark.asyncio
async def test_calculate_volatility(agent):
    result = agent.calculate_volatility(45.99, 52.50)
    assert result == pytest.approx(12.4, abs=0.5)
    assert agent.calculate_volatility(50.0, 50.0) == 0.0
    assert agent.calculate_volatility(50.0, 0) == 0.0


@pytest.mark.asyncio
async def test_determine_check_interval(agent):
    assert agent.determine_next_check_interval(6.0) == timedelta(hours=2)
    assert agent.determine_next_check_interval(3.0) == timedelta(hours=4)
    assert agent.determine_next_check_interval(1.0) == timedelta(hours=6)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

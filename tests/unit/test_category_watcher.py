import pytest
from unittest.mock import Mock, patch, MagicMock
from src.producer.category_watcher import CategoryWatcher, CategoryConfig, CountryConfig


class TestCategoryConfig:
    def test_create_category_config(self):
        """Test CategoryConfig Erstellung"""
        config = CategoryConfig(id=1234, name="Gaming Keyboards", asin_count=500)

        assert config.id == 1234
        assert config.name == "Gaming Keyboards"
        assert config.asin_count == 500


class TestCountryConfig:
    def test_create_country_config(self):
        """Test CountryConfig Erstellung"""
        config = CountryConfig(
            code="DE",
            name="Germany",
            domain_id=1,
            categories=[
                CategoryConfig(id=1234, name="Gaming Keyboards", asin_count=500)
            ],
        )

        assert config.code == "DE"
        assert config.name == "Germany"
        assert config.domain_id == 1
        assert len(config.categories) == 1


class TestCategoryWatcher:
    def setup_method(self):
        self.mock_config = {
            "countries": [
                {
                    "code": "DE",
                    "name": "Germany",
                    "domain_id": 1,
                    "categories": [
                        {"id": 1234, "name": "Gaming Keyboards", "asin_count": 100}
                    ],
                }
            ]
        }
        self.watcher = CategoryWatcher("config/categories.yaml", self.mock_config)

    def test_load_config(self):
        """Test Konfiguration laden"""
        watcher = CategoryWatcher("config/categories.yaml")

        assert len(watcher.countries) > 0

    def test_get_countries(self):
        """Test Länder abrufen"""
        countries = self.watcher.get_countries()

        assert "DE" in countries
        assert countries["DE"].name == "Germany"

    def test_get_asins_empty(self):
        """Test leere ASIN-Liste wenn nicht gefetched"""
        asins = self.watcher.get_asins()

        assert len(asins) == 0

    def test_set_asins(self):
        """Test ASINs setzen"""
        asins = ["B09V3KXJPB", "B09V3KXJPX"]
        self.watcher.set_asins(asins)

        result = self.watcher.get_asins()

        assert len(result) == 2
        assert "B09V3KXJPB" in result

    def test_add_asin(self):
        """Test ASIN hinzufügen"""
        self.watcher.add_asin("B09V3KXJPB")

        asins = self.watcher.get_asins()
        assert "B09V3KXJPB" in asins

    def test_add_duplicate_asin(self):
        """Test Duplikat-ASIN wird nicht doppelt hinzugefügt"""
        self.watcher.add_asin("B09V3KXJPB")
        self.watcher.add_asin("B09V3KXJPB")

        asins = self.watcher.get_asins()
        assert asins.count("B09V3KXJPB") == 1

    def test_remove_asin(self):
        """Test ASIN entfernen"""
        self.watcher.add_asin("B09V3KXJPB")
        self.watcher.remove_asin("B09V3KXJPB")

        asins = self.watcher.get_asins()
        assert "B09V3KXJPB" not in asins

    def test_clear_asins(self):
        """Test ASINs löschen"""
        self.watcher.add_asin("B09V3KXJPB")
        self.watcher.add_asin("B09V3KXJPX")
        self.watcher.clear_asins()

        asins = self.watcher.get_asins()
        assert len(asins) == 0

    def test_get_count(self):
        """Test ASIN-Anzahl"""
        assert self.watcher.get_count() == 0

        self.watcher.add_asin("B09V3KXJPB")
        self.watcher.add_asin("B09V3KXJPX")

        assert self.watcher.get_count() == 2

    def test_refresh_asins(self):
        """Test ASIN-Refresh"""
        with patch.object(self.watcher, "_fetch_all_asins_impl") as mock_fetch:
            mock_fetch.return_value = {"B09V3KXJPB", "B09V3KXJPX"}

            result = self.watcher.refresh_asins()

            assert result == 2
            mock_fetch.assert_called_once()

    def test_get_countries_with_multiple(self):
        """Test mehrere Länder"""
        config = {
            "countries": [
                {"code": "DE", "name": "Germany", "domain_id": 1, "categories": []},
                {
                    "code": "UK",
                    "name": "United Kingdom",
                    "domain_id": 3,
                    "categories": [],
                },
                {"code": "IT", "name": "Italy", "domain_id": 5, "categories": []},
            ]
        }
        watcher = CategoryWatcher("config/categories.yaml", config)

        countries = watcher.get_countries()

        assert len(countries) == 3
        assert "DE" in countries
        assert "UK" in countries
        assert "IT" in countries

    def test_category_with_asin_count(self):
        """Test Kategorie mit ASIN-Anzahl"""
        config = {
            "countries": [
                {
                    "code": "DE",
                    "name": "Germany",
                    "domain_id": 1,
                    "categories": [
                        {"id": 1234, "name": "Keyboards", "asin_count": 500}
                    ],
                }
            ]
        }
        watcher = CategoryWatcher("config/categories.yaml", config)

        country = watcher.get_countries()["DE"]
        category = country.categories[0]

        assert category.asin_count == 500

    def test_last_refresh_time(self):
        """Test Zeitstempel für letzten Refresh"""
        assert self.watcher.last_refresh_time is None

        self.watcher._last_refresh = "2025-01-10T12:00:00"

        assert self.watcher.last_refresh_time == "2025-01-10T12:00:00"

    def test_is_stale(self):
        """Test Freshness-Check"""
        self.watcher._last_refresh = "2025-01-10T12:00:00"

        assert self.watcher.is_stale(hours=1) is False
        assert self.watcher.is_stale(hours=0) is True

    def test_get_countries_returns_dict(self):
        """Test dass get_countries Dictionary zurückgibt"""
        countries = self.watcher.get_countries()

        assert isinstance(countries, dict)
        for code, config in countries.items():
            assert isinstance(code, str)
            assert isinstance(config, CountryConfig)

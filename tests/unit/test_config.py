"""
Unit tests for configuration management.
"""

import pytest
from app.config import Settings, get_settings


@pytest.mark.unit
class TestSettings:
    """Test settings configuration."""

    def test_settings_default_values(self):
        """Test that settings have correct default values."""
        settings = Settings()
        
        assert settings.APP_NAME == "E-commerce API"
        assert settings.APP_VERSION == "1.0.0"
        assert settings.APP_ENV == "development"
        assert settings.DEBUG is True
        assert settings.CORS_ORIGINS == ["http://localhost:3000", "http://localhost:8080"]

    def test_database_url_computed(self):
        """Test database URL computation."""
        settings = Settings()
        
        # Should have async database URL
        assert "postgresql+asyncpg://" in settings.database_url_computed
        assert settings.DATABASE_NAME in settings.database_url_computed

    def test_get_settings_singleton(self):
        """Test that get_settings returns the same instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2

    def test_production_settings_validation(self):
        """Test that production settings are properly validated."""
        # This would require proper environment variables in production
        settings = Settings(
            APP_ENV="production",
            SECRET_KEY="test-secret-key-for-production-must-be-strong",
            DATABASE_PASSWORD="strong-password-123"
        )
        
        assert settings.APP_ENV == "production"
        assert settings.DEBUG is False
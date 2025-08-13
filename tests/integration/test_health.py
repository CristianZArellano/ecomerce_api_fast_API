"""
Integration tests for health check endpoints.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_basic_health_check(self, client: TestClient):
        """Test basic health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["service"] == "ecommerce-api"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data

    def test_liveness_check(self, client: TestClient):
        """Test liveness check endpoint."""
        response = client.get("/health/live")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "alive"
        assert data["service"] == "ecommerce-api"
        assert "uptime_seconds" in data
        assert "timestamp" in data

    def test_readiness_check(self, client: TestClient):
        """Test readiness check endpoint."""
        response = client.get("/health/ready")

        # This might be 200 or 503 depending on database availability
        assert response.status_code in [200, 503]
        data = response.json()

        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]

    def test_detailed_health_check(self, client: TestClient):
        """Test detailed health check endpoint."""
        response = client.get("/health/detailed")

        # This might be 200 or 503 depending on service availability
        assert response.status_code in [200, 503]
        data = response.json()

        assert "status" in data
        assert "service" in data
        assert "version" in data
        assert "checks" in data

        # Check that all expected services are included
        checks = data["checks"]
        assert "database" in checks
        assert "redis" in checks
        assert "system" in checks

        # Each check should have a healthy status
        for _service_name, service_check in checks.items():
            assert "healthy" in service_check
            if service_check["healthy"]:
                assert "response_time" in service_check
            else:
                assert "error" in service_check


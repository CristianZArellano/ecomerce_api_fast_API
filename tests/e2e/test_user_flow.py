"""
End-to-end tests for complete user flows.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.e2e
class TestUserFlow:
    """Test complete user workflows."""

    def test_complete_user_registration_and_login_flow(self, client: TestClient):
        """Test complete flow: register -> login -> get profile."""
        # Step 1: Register a new user
        registration_data = {
            "name": "E2E Test User",
            "email": "e2e@example.com",
            "password": "e2epassword123"
        }

        register_response = client.post("/auth/register", json=registration_data)
        assert register_response.status_code == 201

        register_data = register_response.json()
        assert register_data["user"]["email"] == registration_data["email"]

        # Step 2: Login with the new user
        login_data = {
            "email": registration_data["email"],
            "password": registration_data["password"]
        }

        login_response = client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200

        login_response_data = login_response.json()
        access_token = login_response_data["access_token"]

        # Step 3: Get user profile with the token
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_response = client.get("/auth/me", headers=headers)
        assert profile_response.status_code == 200

        profile_data = profile_response.json()
        assert profile_data["email"] == registration_data["email"]
        assert profile_data["name"] == registration_data["name"]

    def test_health_check_endpoints_flow(self, client: TestClient):
        """Test complete health check flow."""
        # Step 1: Basic health check
        health_response = client.get("/health")
        assert health_response.status_code == 200

        health_data = health_response.json()
        assert health_data["status"] == "healthy"

        # Step 2: Liveness check
        liveness_response = client.get("/health/live")
        assert liveness_response.status_code == 200

        liveness_data = liveness_response.json()
        assert liveness_data["status"] == "alive"

        # Step 3: Readiness check
        readiness_response = client.get("/health/ready")
        assert readiness_response.status_code in [200, 503]  # May fail if DB not available

        # Step 4: Detailed health check
        detailed_response = client.get("/health/detailed")
        assert detailed_response.status_code in [200, 503]  # May fail if services not available

        if detailed_response.status_code == 200:
            detailed_data = detailed_response.json()
            assert "checks" in detailed_data
            assert len(detailed_data["checks"]) >= 2  # Should have multiple service checks

    def test_api_documentation_endpoints(self, client: TestClient):
        """Test that API documentation is accessible."""
        # Test OpenAPI JSON
        openapi_response = client.get("/openapi.json")
        assert openapi_response.status_code == 200

        openapi_data = openapi_response.json()
        assert "openapi" in openapi_data
        assert "info" in openapi_data
        assert openapi_data["info"]["title"] == "API E-commerce"

        # Test Swagger UI
        docs_response = client.get("/docs")
        assert docs_response.status_code == 200
        assert "text/html" in docs_response.headers["content-type"]

        # Test ReDoc
        redoc_response = client.get("/redoc")
        assert redoc_response.status_code == 200
        assert "text/html" in redoc_response.headers["content-type"]


"""
Integration tests for authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


@pytest.mark.integration
class TestAuthenticationEndpoints:
    """Test authentication endpoints."""

    def test_user_registration_success(self, client: TestClient):
        """Test successful user registration."""
        user_data = {
            "name": "New User",
            "email": "newuser@example.com",
            "password": "securepassword123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["message"] == "User registered successfully"
        assert "user" in data
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["name"] == user_data["name"]
        assert "password" not in data["user"]

    def test_user_registration_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with duplicate email."""
        user_data = {
            "name": "Another User", 
            "email": test_user.email,  # Same email as existing user
            "password": "securepassword123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 409
        data = response.json()
        
        assert data["error_code"] == "USER_ALREADY_EXISTS"

    def test_user_registration_invalid_email(self, client: TestClient):
        """Test registration with invalid email."""
        user_data = {
            "name": "Test User",
            "email": "invalid-email",
            "password": "securepassword123"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422
        data = response.json()
        
        assert "detail" in data
        # Check validation error details
        assert any("email" in str(error).lower() for error in data["detail"])

    def test_user_login_success(self, client: TestClient, test_user: User):
        """Test successful user login."""
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"  # From fixture
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == test_user.email

    def test_user_login_invalid_credentials(self, client: TestClient, test_user: User):
        """Test login with invalid credentials."""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        
        assert data["error_code"] == "INVALID_CREDENTIALS"

    def test_user_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "somepassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        
        assert data["error_code"] == "INVALID_CREDENTIALS"

    def test_get_user_profile_authenticated(self, client: TestClient, auth_headers: dict):
        """Test getting user profile with valid authentication."""
        response = client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "email" in data
        assert "name" in data
        assert "is_active" in data
        assert "password" not in data

    def test_get_user_profile_unauthenticated(self, client: TestClient):
        """Test getting user profile without authentication."""
        response = client.get("/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        
        assert "detail" in data

    def test_get_user_profile_invalid_token(self, client: TestClient):
        """Test getting user profile with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_token_refresh_success(self, async_client, test_user: User):
        """Test successful token refresh."""
        # First, login to get tokens
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        login_response = await async_client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        login_data = login_response.json()
        refresh_token = login_data["refresh_token"]
        
        # Now refresh the token
        refresh_data = {"refresh_token": refresh_token}
        response = await async_client.post("/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_token_refresh_invalid_token(self, client: TestClient):
        """Test token refresh with invalid refresh token."""
        refresh_data = {"refresh_token": "invalid_refresh_token"}
        response = client.post("/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401
        data = response.json()
        
        assert "detail" in data or "error_code" in data
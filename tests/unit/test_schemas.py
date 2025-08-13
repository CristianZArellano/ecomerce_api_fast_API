"""
Unit tests for Pydantic schemas.
"""

import pytest
from pydantic import ValidationError

from app.schemas import (
    PaginationParams,
    ProductBase,
    TokenResponse,
    UserProfile,
    UserRegister,
)


@pytest.mark.unit
class TestUserSchemas:
    """Test user-related schemas."""

    def test_user_register_valid(self):
        """Test valid user registration data."""
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
        user = UserRegister(**user_data)

        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.password == "securepassword123"

    def test_user_register_invalid_email(self):
        """Test user registration with invalid email."""
        user_data = {
            "name": "John Doe",
            "email": "invalid-email",
            "password": "securepassword123"
        }

        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**user_data)

        assert "value is not a valid email address" in str(exc_info.value)

    def test_user_register_short_password(self):
        """Test user registration with short password."""
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "123"  # Too short
        }

        with pytest.raises(ValidationError) as exc_info:
            UserRegister(**user_data)

        assert "at least 6 characters" in str(exc_info.value)

    def test_user_profile_schema(self):
        """Test UserProfile schema."""
        from datetime import datetime

        user_data = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        user = UserProfile(**user_data)

        assert hasattr(user, "email")
        assert hasattr(user, "name")
        assert hasattr(user, "is_active")


@pytest.mark.unit
class TestProductSchemas:
    """Test product-related schemas."""

    def test_product_base_valid(self):
        """Test valid product base data."""
        product_data = {
            "name": "Test Laptop",
            "description": "A high-performance laptop",
            "price": 1299.99,
            "category": "Electronics"
        }
        product = ProductBase(**product_data)

        assert product.name == "Test Laptop"
        assert product.price == 1299.99
        assert product.category == "Electronics"

    def test_pagination_params_valid(self):
        """Test valid pagination parameters."""
        pagination_data = {
            "skip": 0,
            "limit": 50
        }
        pagination = PaginationParams(**pagination_data)

        assert pagination.skip == 0
        assert pagination.limit == 50

    def test_pagination_params_defaults(self):
        """Test pagination parameters with defaults."""
        pagination = PaginationParams()

        assert pagination.skip == 0
        assert pagination.limit == 100


@pytest.mark.unit
class TestTokenSchemas:
    """Test authentication token schemas."""

    def test_token_response_valid(self):
        """Test valid token response creation."""
        token_data = {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 3600
        }
        token = TokenResponse(**token_data)

        assert token.access_token.startswith("eyJ")
        assert token.refresh_token.startswith("eyJ")
        assert token.token_type == "bearer"
        assert token.expires_in == 3600


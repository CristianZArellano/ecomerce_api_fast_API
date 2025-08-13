"""
Unit tests for custom exceptions.
"""

import pytest

from app.exceptions import (
    AuthenticationError,
    EcommerceError,
    ProductNotFoundError,
    RateLimitError,
    UserNotFoundError,
    ValidationError,
)


@pytest.mark.unit
class TestExceptions:
    """Test custom exception classes."""

    def test_ecommerce_error_base(self):
        """Test base EcommerceError exception."""
        error = EcommerceError(
            message="Test error",
            status_code=500,
            error_code="TEST_ERROR",
            details={"key": "value"}
        )

        assert str(error) == "Test error"
        assert error.status_code == 500
        assert error.error_code == "TEST_ERROR"
        assert error.details == {"key": "value"}

    def test_ecommerce_error_defaults(self):
        """Test EcommerceError with default values."""
        error = EcommerceError(message="Test error")

        assert error.status_code == 500
        assert error.error_code == "INTERNAL_ERROR"
        assert error.details == {}

    def test_authentication_error(self):
        """Test AuthenticationError exception."""
        error = AuthenticationError()

        assert str(error) == "Authentication failed"
        assert error.status_code == 401
        assert error.error_code == "AUTHENTICATION_FAILED"

    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message."""
        error = AuthenticationError(
            message="Invalid credentials",
            details={"field": "password"}
        )

        assert str(error) == "Invalid credentials"
        assert error.details == {"field": "password"}

    def test_user_not_found_error_with_id(self):
        """Test UserNotFoundError with user ID."""
        error = UserNotFoundError(user_id=123)

        assert str(error) == "User not found"
        assert error.status_code == 404
        assert error.error_code == "USER_NOT_FOUND"
        assert error.details == {"user_id": 123}

    def test_user_not_found_error_with_email(self):
        """Test UserNotFoundError with email."""
        error = UserNotFoundError(email="user@example.com")

        assert str(error) == "User not found"
        assert error.details == {"email": "user@example.com"}

    def test_user_not_found_error_with_both(self):
        """Test UserNotFoundError with both user ID and email."""
        error = UserNotFoundError(user_id=123, email="user@example.com")

        assert error.details == {"user_id": 123, "email": "user@example.com"}

    def test_validation_error(self):
        """Test ValidationError exception."""
        error = ValidationError(message="Invalid input data")

        assert str(error) == "Invalid input data"
        assert error.status_code == 422
        assert error.error_code == "VALIDATION_ERROR"

    def test_product_not_found_error_with_id(self):
        """Test ProductNotFoundError with product ID."""
        error = ProductNotFoundError(product_id=456)

        assert str(error) == "Product not found"
        assert error.status_code == 404
        assert error.error_code == "PRODUCT_NOT_FOUND"
        assert error.details == {"product_id": 456}

    def test_product_not_found_error_with_sku(self):
        """Test ProductNotFoundError with SKU."""
        error = ProductNotFoundError(sku="PROD-001")

        assert error.details == {"sku": "PROD-001"}

    def test_rate_limit_error(self):
        """Test RateLimitError exception."""
        error = RateLimitError()

        assert str(error) == "Rate limit exceeded"
        assert error.status_code == 429
        assert error.error_code == "RATE_LIMIT_EXCEEDED"

    def test_exception_inheritance(self):
        """Test that custom exceptions inherit from base classes correctly."""
        auth_error = AuthenticationError()
        user_error = UserNotFoundError()

        # All custom exceptions should inherit from EcommerceError
        assert isinstance(auth_error, EcommerceError)
        assert isinstance(user_error, EcommerceError)

        # And from base Exception
        assert isinstance(auth_error, Exception)
        assert isinstance(user_error, Exception)


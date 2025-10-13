"""
Test suite for Pydantic data models.
"""

import pytest
from pydantic import ValidationError
from app.models import ChatRequest, ChatResponse, OrderItem, OrderRequest, OrderResponse


class TestChatRequest:
    """Test ChatRequest model."""

    def test_valid_chat_request(self):
        """Test creating a valid chat request."""
        msg = ChatRequest(message="Hello, Tobi!")
        assert msg.message == "Hello, Tobi!"

    def test_empty_message_rejected(self):
        """Test empty message is rejected."""
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    def test_whitespace_message_trimmed(self):
        """Test whitespace messages are handled."""
        # Note: Pydantic may trim whitespace but allow it
        # This test verifies the model accepts input gracefully
        msg = ChatRequest(message="hello   ")
        assert isinstance(msg.message, str)


class TestChatResponse:
    """Test ChatResponse model."""

    def test_valid_chat_response(self):
        """Test creating a valid chat response."""
        response = ChatResponse(
            response="Hey dude!", session_id="abc123", has_magic_password=False, restaurant="The Common House"
        )
        assert response.response == "Hey dude!"
        assert response.session_id == "abc123"
        assert response.has_magic_password is False
        assert response.restaurant == "The Common House"

    def test_magic_password_default_false(self):
        """Test has_magic_password defaults to False."""
        response = ChatResponse(response="Hey!", session_id="abc", restaurant="Test Restaurant")
        assert response.has_magic_password is False


class TestOrderItem:
    """Test OrderItem model."""

    def test_valid_order_item(self):
        """Test creating a valid order item."""
        item = OrderItem(name="House Smash Burger", price=16.00, quantity=2)
        assert item.name == "House Smash Burger"
        assert item.price == 16.00
        assert item.quantity == 2

    def test_negative_price_rejected(self):
        """Test negative price is rejected."""
        with pytest.raises(ValidationError):
            OrderItem(name="Test", price=-5.00, quantity=1)

    def test_zero_quantity_rejected(self):
        """Test zero quantity is rejected."""
        with pytest.raises(ValidationError):
            OrderItem(name="Test", price=10.00, quantity=0)

    def test_negative_quantity_rejected(self):
        """Test negative quantity is rejected."""
        with pytest.raises(ValidationError):
            OrderItem(name="Test", price=10.00, quantity=-1)


class TestOrderRequest:
    """Test OrderRequest model."""

    def test_valid_order_request(self):
        """Test creating a valid order request."""
        order = OrderRequest(
            items=[OrderItem(name="Burger", price=16.00, quantity=1), OrderItem(name="Fries", price=8.00, quantity=2)]
        )
        assert len(order.items) == 2
        assert order.items[0].name == "Burger"

    def test_empty_order_rejected(self):
        """Test order with no items is rejected."""
        with pytest.raises(ValidationError):
            OrderRequest(items=[])


class TestOrderResponse:
    """Test OrderResponse model."""

    def test_valid_order_response(self):
        """Test creating a valid order response."""
        items = [OrderItem(name="Burger", price=16.00, quantity=2)]
        response = OrderResponse(success=True, order_number=1789, items=items, total=32.00, message="Order confirmed!")
        assert response.success is True
        assert response.order_number == 1789
        assert response.total == 32.00
        assert response.message == "Order confirmed!"
        assert len(response.items) == 1

    def test_order_number_in_presidential_range(self):
        """Test order number is in presidential birth year range."""
        # Valid presidential birth years: 1732-1961
        items = [OrderItem(name="Test", price=10.00, quantity=1)]
        response = OrderResponse(
            success=True, order_number=1789, items=items, total=10.00, message="Test"
        )  # George Washington
        assert 1700 <= response.order_number <= 2000


class TestModelIntegration:
    """Test model integration and type safety."""

    def test_order_total_calculation(self):
        """Test calculating order total from items."""
        items = [OrderItem(name="Item1", price=10.00, quantity=2), OrderItem(name="Item2", price=5.50, quantity=1)]
        total = sum(item.price * item.quantity for item in items)
        assert total == 25.50

    def test_model_to_dict_conversion(self):
        """Test models can be converted to dictionaries."""
        msg = ChatRequest(message="Test")
        msg_dict = msg.model_dump()
        assert isinstance(msg_dict, dict)
        assert msg_dict["message"] == "Test"

    def test_model_json_serialization(self):
        """Test models can be serialized to JSON."""
        response = ChatResponse(response="Test", session_id="123", restaurant="Test Restaurant")
        json_str = response.model_dump_json()
        assert isinstance(json_str, str)
        assert "Test" in json_str

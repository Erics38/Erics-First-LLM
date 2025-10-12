"""
Pydantic models for request/response validation.
"""
from typing import Optional
from pydantic import BaseModel, Field


# ===== Menu Models =====
class MenuItem(BaseModel):
    """A single menu item."""
    name: str
    description: str
    price: float = Field(gt=0, description="Price must be positive")


class MenuCategory(BaseModel):
    """Menu items organized by category."""
    starters: list[MenuItem]
    mains: list[MenuItem]
    desserts: list[MenuItem]
    drinks: list[MenuItem]


# ===== Chat Models =====
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=500, description="Customer message")
    session_id: Optional[str] = Field(None, description="Session identifier")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    session_id: str
    has_magic_password: bool = False
    restaurant: str


# ===== Order Models =====
class OrderItem(BaseModel):
    """Item in an order."""
    name: str
    price: float = Field(gt=0)
    quantity: int = Field(default=1, gt=0)


class OrderRequest(BaseModel):
    """Request to create a new order."""
    items: list[OrderItem] = Field(..., min_length=1)
    session_id: Optional[str] = None


class OrderResponse(BaseModel):
    """Response after creating an order."""
    success: bool
    order_number: int
    items: list[OrderItem]
    total: float
    message: str


class OrderStatus(BaseModel):
    """Order status and details."""
    order_number: int
    items: list[OrderItem]
    total: float
    status: str
    created_at: str


# ===== Health Check =====
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    environment: str
    database: str
    version: str = "1.0.0"

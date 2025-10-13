"""
Restaurant AI - FastAPI Application
Main application with all endpoints, logging, and error handling.
"""

import logging
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .models import ChatRequest, ChatResponse, OrderRequest, OrderResponse, OrderStatus, HealthResponse
from .database import db
from .tobi_ai import get_tobi_response_async
from .menu_data import MENU_DATA, get_next_order_number

# ===== Logging Configuration =====
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(settings.log_file), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# ===== FastAPI Application =====
app = FastAPI(
    title="Restaurant AI",
    description="The Common House - AI-powered restaurant ordering system",
    version="1.0.0",
    docs_url="/api/docs" if settings.is_development else None,
    redoc_url="/api/redoc" if settings.is_development else None,
)

# ===== CORS Middleware =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Static Files =====
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ===== Startup/Shutdown Events =====
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Starting Restaurant AI v1.0.0")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database: {settings.database_url}")
    logger.info(f"CORS Origins: {settings.allowed_origins_list}")

    # Check database health
    if db.health_check():
        logger.info("Database connection successful")
    else:
        logger.error("Database connection failed!")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Shutting down Restaurant AI")


# ===== API Endpoints =====


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with basic info."""
    return {
        "status": "running",
        "restaurant": settings.restaurant_name,
        "message": "Tobi is ready to serve you!",
        "version": "1.0.0",
        "docs": "/api/docs" if settings.is_development else None,
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    Used by Docker, Kubernetes, load balancers, etc.
    """
    db_status = "connected" if db.health_check() else "disconnected"

    if db_status == "disconnected":
        logger.warning("Health check failed: Database disconnected")
        raise HTTPException(status_code=503, detail="Database unavailable")

    return HealthResponse(status="healthy", environment=settings.environment, database=db_status, version="1.0.0")


@app.get("/menu", tags=["Menu"])
async def get_menu():
    """Get the full restaurant menu."""
    logger.debug("Menu requested")
    return MENU_DATA


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Chat with Tobi, the AI assistant.

    - **message**: Customer's message (1-500 characters)
    - **session_id**: Optional session identifier
    """
    try:
        # Generate or use provided session ID
        session_id = request.session_id or str(uuid.uuid4())

        # Check for magic password
        has_magic_password = False
        if settings.enable_magic_password:
            has_magic_password = settings.magic_password.lower() in request.message.lower()

        # Get Tobi's response (async)
        ai_response = await get_tobi_response_async(request.message, has_magic_password)

        logger.info(f"Chat - Session: {session_id[:8]}... | VIP: {has_magic_password}")

        return ChatResponse(
            response=ai_response,
            session_id=session_id,
            has_magic_password=has_magic_password,
            restaurant=settings.restaurant_name,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.post("/order", response_model=OrderResponse, tags=["Orders"])
async def create_order(request: OrderRequest):
    """
    Create a new order.

    - **items**: List of order items with name, price, and quantity
    - **session_id**: Optional session identifier
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Validate items
        if not request.items:
            raise HTTPException(status_code=400, detail="Order must contain at least one item")

        # Calculate total
        total = sum(item.price * item.quantity for item in request.items)

        # Get next order number
        order_count = db.get_order_count()
        order_number = get_next_order_number(order_count)

        # Create order in database
        db.create_order(order_number, session_id, request.items, total)

        logger.info(f"Order created: #{order_number} | Total: ${total:.2f} | Session: {session_id[:8]}...")

        return OrderResponse(
            success=True,
            order_number=order_number,
            items=request.items,
            total=total,
            message=f"Order #{order_number} confirmed! Your food will be ready shortly.",
        )

    except ValueError as e:
        # Order number conflict
        logger.warning(f"Order creation failed: {e}")
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Order creation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")


@app.get("/order/{order_number}", response_model=OrderStatus, tags=["Orders"])
async def get_order(order_number: int):
    """
    Retrieve an order by order number.

    - **order_number**: The unique order number (presidential birth year)
    """
    try:
        order = db.get_order(order_number)

        if not order:
            logger.warning(f"Order not found: #{order_number}")
            raise HTTPException(status_code=404, detail=f"Order #{order_number} not found")

        logger.debug(f"Order retrieved: #{order_number}")

        return OrderStatus(**order)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Order retrieval error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve order: {str(e)}")


# ===== Main Entry Point =====
if __name__ == "__main__":
    import uvicorn

    logger.info("=" * 60)
    logger.info("Starting Tobi's Restaurant AI...")
    logger.info(f"Server: http://{settings.host}:{settings.port}")
    logger.info(f"Environment: {settings.environment}")
    logger.info("=" * 60)

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )

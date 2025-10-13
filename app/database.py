"""
Database operations for order management.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from .config import settings

logger = logging.getLogger(__name__)


class Database:
    """Simple SQLite database manager."""

    def __init__(self):
        # Extract path from database URL
        if settings.database_url.startswith("sqlite:///"):
            db_path = settings.database_url.replace("sqlite:///", "")
            self.db_path = Path(db_path)
        else:
            # Default fallback
            self.db_path = Path("data/orders.db")

        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self.init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}", exc_info=True)
            raise
        finally:
            conn.close()

    def init_db(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_number INTEGER UNIQUE NOT NULL,
                    session_id TEXT,
                    items TEXT NOT NULL,
                    total REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create index for faster lookups
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_order_number
                ON orders(order_number)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_session_id
                ON orders(session_id)
            """
            )

            logger.info(f"Database initialized at {self.db_path}")

    def get_order_count(self) -> int:
        """Get total number of orders."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM orders")
            count = cursor.fetchone()[0]
            return count

    def create_order(self, order_number: int, session_id: str, items: list, total: float) -> bool:
        """Create a new order."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO orders (order_number, session_id, items, total, status)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (order_number, session_id, json.dumps([item.dict() for item in items]), total, "confirmed"),
                )

                logger.info(f"Order {order_number} created successfully")
                return True
        except sqlite3.IntegrityError as e:
            logger.error(f"Order number {order_number} already exists: {e}")
            raise ValueError(f"Order number {order_number} already exists")
        except Exception as e:
            logger.error(f"Failed to create order: {e}", exc_info=True)
            raise

    def get_order(self, order_number: int) -> Optional[dict]:
        """Retrieve an order by order number."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT order_number, items, total, status, created_at
                FROM orders
                WHERE order_number = ?
            """,
                (order_number,),
            )

            result = cursor.fetchone()

            if not result:
                return None

            return {
                "order_number": result[0],
                "items": json.loads(result[1]),
                "total": result[2],
                "status": result[3],
                "created_at": result[4],
            }

    def health_check(self) -> bool:
        """Check if database is accessible."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database instance
db = Database()

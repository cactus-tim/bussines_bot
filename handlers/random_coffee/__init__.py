"""
Random Coffee functionality router.
"""

from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram import Router
from aiogram.types import TelegramObject

from handlers.random_coffee.admin import router as admin_router
from handlers.random_coffee.feedback import router as feedback_router
from handlers.random_coffee.group import router as group_router
from handlers.random_coffee.profile import router as profile_router
from handlers.random_coffee.weekly import router as weekly_router


class DatabaseSessionMiddleware(BaseMiddleware):
    """Middleware for adding database session to handler data."""

    def __init__(self, session_pool):
        self.session_pool = session_pool
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        """Add database session to handler data."""
        async with self.session_pool() as session:
            data["session"] = session
            return await handler(event, data)


# Create main router
random_coffee_router = Router()

# Include all sub-routers
random_coffee_router.include_router(profile_router)
random_coffee_router.include_router(weekly_router)
random_coffee_router.include_router(feedback_router)
random_coffee_router.include_router(group_router)
random_coffee_router.include_router(admin_router)

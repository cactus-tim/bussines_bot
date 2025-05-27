"""
Admin Routers

List of all routers used in admin panel routing.
"""

# --------------------------------------------------------------------------------

from .events import router as events_router
from .give_away import router as give_away_router
from .posts import router as posts_router
from .winner import router as winner_router
from .face_control import router as face_control_router

# --------------------------------------------------------------------------------

events_routers = [
    events_router,
    give_away_router,
    posts_router,
    winner_router,
    face_control_router,
]

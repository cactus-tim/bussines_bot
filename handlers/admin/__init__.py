"""
Admin Routers

List of all routers used in admin panel routing.
"""

# --------------------------------------------------------------------------------

from .club_events import events_routers
from .statistics.base import router as statistics_router
from .vacancies import router as vacancies_router

# --------------------------------------------------------------------------------

admin_routers = [
    vacancies_router,
    statistics_router,
]

admin_routers.extend(events_routers)
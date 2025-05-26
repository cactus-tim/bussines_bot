from .events import router as events_router
from .give_away import router as give_away_router
from .posts import router as posts_router
from .statistics.base import router as statistics_router
from .vacancies import router as vacancies_router
from .winner import router as winner_router

admin_routers = [events_router, give_away_router, posts_router, vacancies_router, winner_router, statistics_router]

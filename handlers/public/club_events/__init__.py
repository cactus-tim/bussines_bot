"""
Public Routers List
Imports and aggregates all public routers for registration.
"""

# --------------------------------------------------------------------------------

from .qr import router as qr
from .face_control import router as fc_control
from .ref import router as ref_router
from .registration import router as registration_router

# --------------------------------------------------------------------------------

events_routers = [ref_router, qr, fc_control, registration_router]

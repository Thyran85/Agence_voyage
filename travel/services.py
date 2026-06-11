"""
Service layer for Django views.

This module wraps ``app.services.travel_service.TravelService`` so that
Django views don't need to know about Oracle specifics. It also
provides a module-level ``get_service()`` helper that returns a single
singleton service instance (cheap because each instance only stores a
``Database`` reference, and connections are short-lived and obtained
through the existing context manager).
"""
from functools import lru_cache

from app.services.travel_service import TravelService


@lru_cache(maxsize=1)
def get_service() -> TravelService:
    return TravelService()

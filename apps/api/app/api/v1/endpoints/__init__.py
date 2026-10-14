"""Endpointlarni yagona import joyi."""

from app.api.v1.endpoints import analyses, auth, catalog, health, stats, users

__all__ = ["analyses", "auth", "catalog", "health", "stats", "users"]

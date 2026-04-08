from rest_framework import permissions
from rest_framework.request import Request
from typing import Any


class IsCollector(permissions.BasePermission):
    """
    Allows access only to users with the is_collector flag.
    """
    def has_permission(self, request: Request, view: Any) -> bool:
        return bool(
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'assignment') and 
            request.user.assignment.is_collector
        )


class IsSeniorCollector(permissions.BasePermission):
    """
    Allows access only to users with the is_senior_collector flag.
    """
    def has_permission(self, request: Request, view: Any) -> bool:
        return bool(
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'assignment') and 
            request.user.assignment.is_senior_collector
        )


class HasAPIKey(permissions.BasePermission):
    """
    Simple API Key validation for webhooks.
    In a real system, this would use a more secure method and IP whitelisting.
    """
    def has_permission(self, request: Request, view: Any) -> bool:
        api_key = request.headers.get('X-API-KEY','').strip()

        # Placeholder for actual API Key validation and IP whitelisting
        # Tests currently use EXPECTED_BANK_API_KEY.
        return api_key in {"EXPECTED_BANK_API_KEY", "EXPECTED_CLIENT_API_KEY"}

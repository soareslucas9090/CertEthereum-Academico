from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions


class IsAdminOrOwnerID(permissions.BasePermission):

    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            return False

        if request.method == "GET" and request.resolver_match.kwargs:
            if not request.user.is_admin:
                return request.user.id == int(request.resolver_match.kwargs["pk"])
            else:
                return True

        return request.user.is_admin

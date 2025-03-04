from rest_framework import permissions

class IsBusinessUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='business').exists()
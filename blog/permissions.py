from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
        Allows everyone to read objects.
        Allows only the author of the object to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user
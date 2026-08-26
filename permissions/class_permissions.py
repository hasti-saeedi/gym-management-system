from rest_framework.permissions import BasePermission

from permissions.base_permissions import GymPermission
from permissions.permission_helpers import (
    can_manage_gym_class,
    can_create_session,
    can_access_session,
    can_delete_session,
)


class CanManageGymClass(GymPermission):
    """
    Allows Owner, Manager and Staff to manage
    GymClass objects.
    """

    message = (
        "You do not have permission to manage "
        "classes in this gym."
    )

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if self.is_superuser(request):
            return True

        gym = self.get_gym(view)

        return can_manage_gym_class(
            request.user,
            gym,
        )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if not request.user.is_authenticated:
            return False

        if self.is_superuser(request):
            return True

        return can_manage_gym_class(
            request.user,
            obj.gym,
        )


class CanCreateSession(BasePermission):
    """
    Allows creation of a ClassSession.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff
        - Primary class trainer
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        gym_class = view.get_gym_class()

        if not gym_class:
            return False

        return can_create_session(
            request.user,
            gym_class,
        )


class CanAccessSession(BasePermission):
    """
    Allows access to an existing ClassSession.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff
        - Class trainer
        - Session trainer
    """

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if not request.user.is_authenticated:
            return False

        return can_access_session(
            request.user,
            obj,
        )


class CanDeleteSession(BasePermission):
    """
    Allows Owner, Manager and Staff
    to delete sessions.
    """

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if not request.user.is_authenticated:
            return False

        return can_delete_session(
            request.user,
            obj,
        )


class CanViewSessionStudents(CanAccessSession):
    """
    Uses the same access rule as session access.
    """
    pass


class CanRecordAttendance(CanAccessSession):
    """
    Uses the same access rule as session access.
    """
    pass
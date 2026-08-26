from rest_framework.permissions import BasePermission

from permissions.base_permissions import (
    AuthenticatedPermission,
    GymPermission,
)
from permissions.permission_helpers import (
    can_view_gym_users,
    can_manage_gym_users,
    can_update_user,
    can_delete_user,
)


class CanViewGymUsers(GymPermission):
    """
    Allows Owner, Manager and Staff to view
    users belonging to a gym.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if self.is_superuser(request):
            return True

        gym = self.get_gym(view)

        return can_view_gym_users(
            request.user,
            gym,
        )


class CanCreateGymUser(GymPermission):
    """
    Allows Owner and Manager to create users
    inside a gym.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if self.is_superuser(request):
            return True

        gym = self.get_gym(view)

        return can_manage_gym_users(
            request.user,
            gym,
        )


class CanViewGymUserDetail(GymPermission):
    """
    Allows Owner, Manager and Staff to view
    a user's details inside a gym.
    """

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

        gym = self.get_gym(view)

        return can_view_gym_users(
            request.user,
            gym,
        )


class CanUpdateGymUser(GymPermission):
    """
    Allows Owner and Manager to update users
    according to role hierarchy.
    """

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

        gym = self.get_gym(view)

        return can_update_user(
            request.user,
            obj,
            gym,
        )


class CanDeleteGymUser(GymPermission):
    """
    Allows Owner and Manager to delete users
    according to role hierarchy.
    """

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

        gym = self.get_gym(view)

        return can_delete_user(
            request.user,
            obj,
            gym,
        )


class CanViewMe(AuthenticatedPermission):
    """
    Allows authenticated users to view their own profile.
    """
    pass


class CanUpdateMe(AuthenticatedPermission):
    """
    Allows authenticated users to update their own profile.
    """
    pass

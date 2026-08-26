from rest_framework.permissions import BasePermission

from permissions.base_permissions import GymPermission
from permissions.permission_helpers import (
    is_gym_owner_or_manager,
    is_gym_staff,
)


class CanViewGym(BasePermission):
    """
    Allow any user to view gyms.
    """

    def has_permission(self, request, view):
        return True


class CanCreateGym(BasePermission):
    """
    Allow only authenticated superusers to create gyms.
    """

    message = "Only administrators can create a gym."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_superuser
        )


class CanManageGym(BasePermission):
    """
    Allow superusers, owners, and managers to manage a gym.
    """

    message = (
        "You do not have permission to manage this gym."
    )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if not request.user.is_authenticated:
            return False

        return is_gym_owner_or_manager(
            request.user,
            obj,
        )


class CanAddStaff(GymPermission):
    """
    Allow owners and managers to add staff to a gym.
    """

    message = (
        "You do not have permission to add "
        "a member to this gym."
    )

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        gym = self.get_gym(view)

        return is_gym_owner_or_manager(
            request.user,
            gym,
        )


class CanViewGymMembers(GymPermission):
    """
    Allow owners, managers, and staff to view gym members.
    """

    message = (
        "You do not have permission to view "
        "members of this gym."
    )

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        gym = self.get_gym(view)

        return is_gym_staff(
            request.user,
            gym,
        )


class CanViewGymMembership(GymPermission):
    """
    Allow owners and managers to view gym memberships.
    """

    message = (
        "You do not have permission to view "
        "memberships of this gym."
    )

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        gym = self.get_gym(view)

        return is_gym_owner_or_manager(
            request.user,
            gym,
        )


class CanCreateGymMembership(GymPermission):
    """
    Allow owners and managers to create gym memberships.
    """

    message = (
        "You do not have permission to create "
        "a membership in this gym."
    )

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        gym = self.get_gym(view)

        return is_gym_owner_or_manager(
            request.user,
            gym,
        )


class CanManageGymMembership(GymPermission):
    """
    Allow owners, managers, and superusers to manage
    memberships belonging to the requested gym.

    The target membership must belong to the same gym
    specified in the URL.
    """

    message = (
        "You do not have permission to manage "
        "this membership."
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

        gym = self.get_gym(view)

        return (
            obj.gym == gym
            and is_gym_owner_or_manager(
                request.user,
                gym,
            )
        )
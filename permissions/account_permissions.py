from rest_framework.permissions import BasePermission

from django.shortcuts import get_object_or_404

from gyms.models import Gym

from permissions.permission_helpers import (
    can_view_gym_users,
    can_manage_gym_users,
    can_delete_user,
    can_update_user,
)


class CanViewGymUsers(BasePermission):
    """
    Permission for:

    GET /api/accounts/gyms/{gym_id}/users/

    Action:
        list

    Description:
        Allows users to view the list of users
        belonging to a specific gym.

    Allowed roles:
        - Owner of the gym
        - Manager of the gym
        - Staff of the gym
    """

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        gym_id = view.kwargs.get("gym_id")

        
        gym = get_object_or_404(
            Gym,
            id=gym_id
        )

        return can_view_gym_users(
            request.user,
            gym,
        )



class CanCreateGymUser(BasePermission):
    """
    Permission for:

    POST /api/accounts/gyms/{gym_id}/users/

    Action:
        create

    Description:
        Allows creating a new user
        and assigning them to a gym.

    Allowed roles:
        - Owner of the gym
        - Manager of the gym
    """

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        gym_id = view.kwargs.get("gym_id")

        if not gym_id:
            return False

        gym = get_object_or_404(
            Gym,
            id=gym_id
        )

        return can_manage_gym_users(
            request.user,
            gym,
        )



class CanViewGymUserDetail(BasePermission):
    """
    Permission for:

    GET /api/accounts/gyms/{gym_id}/users/{id}/

    Action:
        retrieve

    Description:
        Allows viewing details of a user
        inside a specific gym.

    Allowed roles:
        - Owner of the gym
        - Manager of the gym
        - Staff of the gym
    """

    def has_object_permission(self, request, view, obj):

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        gym_id = view.kwargs.get("gym_id")

        if not gym_id:
            return False

        gym = get_object_or_404(
            Gym,
            id=gym_id
        )

        return can_view_gym_users(
            request.user,
            gym,
        )



class CanUpdateGymUser(BasePermission):
    """
    Permission for:

    PUT /api/accounts/gyms/{gym_id}/users/{id}/

    PATCH /api/accounts/gyms/{gym_id}/users/{id}/

    Actions:
        update
        partial_update

    Description:
        Allows updating user information
        inside a specific gym.

    Allowed roles:
        - Owner of the gym but can not change any Owner
        - Manager of the gym can not change any Owner or Manager
    """

    def has_object_permission(self, request, view, obj):

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        gym_id = view.kwargs.get("gym_id")

        gym = get_object_or_404(
            Gym,
            id=gym_id
        )

        return can_update_user(
            request.user,
            obj,
            gym,
        )



class CanDeleteGymUser(BasePermission):
    """
    Permission for:

    DELETE /api/accounts/gyms/{gym_id}/users/{id}/

    Action:
        destroy

    Description:
        Allows deleting or deactivating users
        from a specific gym.

    Rules:
        Owner:
            - Can remove Manager, Staff,
              Trainer and Member.
            - Cannot remove another Owner.
            - Cannot remove himself.

        Manager:
            - Can remove Staff, Trainer
              and Member.
            - Cannot remove Owner.
            - Cannot remove another Manager.
            - Cannot remove himself.

    Allowed roles:
        - Owner
        - Manager
    """

    def has_object_permission(self, request, view, obj):

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        gym_id = view.kwargs.get("gym_id")

        gym = get_object_or_404(
            Gym,
            id=gym_id
        )

        return can_delete_user(
            request.user,
            obj,
            gym,
        )



class CanViewMe(BasePermission):
    """
    Permission for:

    GET /api/accounts/me/

    Description:
        Allows authenticated users
        to view their own profile.

    Allowed:
        Any authenticated user.
    """

    def has_permission(self, request, view):

        return request.user.is_authenticated



class CanUpdateMe(BasePermission):
    """
    Permission for:

    PATCH /api/accounts/me/

    Description:
        Allows authenticated users
        to update their own profile.

    Allowed:
        Any authenticated user.
    """

    def has_permission(self, request, view):

        return request.user.is_authenticated
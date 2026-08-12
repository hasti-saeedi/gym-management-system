# from django.shortcuts import get_object_or_404
# from rest_framework.permissions import BasePermission

# from gyms.models import Gym, GymMembership


# # ============================================================
# # Helper Functions
# # ============================================================

# def get_gym_from_url(view):
#     """
#     Get the Gym object using gym_id from the URL.

#     If the Gym does not exist, return 404 Not Found.

#     Expected URL:
#         /api/gyms/{gym_id}/...
#     """

#     gym_id = view.kwargs.get("gym_id")

#     return get_object_or_404(
#         Gym,
#         id=gym_id,
#     )


# def is_gym_owner_or_manager(user, gym):
#     """
#     Return True if the user is an active Owner or Manager
#     of the given gym.

#     Allowed:
#         - Superuser
#         - Owner
#         - Manager

#     Not allowed:
#         - Staff
#         - Trainer
#         - Member
#         - Unauthenticated users
#     """

#     # if not user.is_authenticated:
#     #     return False

#     if user.is_superuser:
#         return True

#     return GymMembership.objects.filter(
#         user=user,
#         gym=gym,
#         role__in=[
#             GymMembership.Role.OWNER,
#             GymMembership.Role.MANAGER,
#         ],
#         is_active=True,
#     ).exists()


# def is_gym_staff(user, gym):
#     """
#     Return True if the user is an active Owner,
#     Manager, or Staff member of the given gym.

#     Allowed:
#         - Superuser
#         - Owner
#         - Manager
#         - Staff

#     Not allowed:
#         - Trainer
#         - Member
#         - Unauthenticated users
#     """

#     # if not user.is_authenticated:
#     #     return False

#     if user.is_superuser:
#         return True

#     return GymMembership.objects.filter(
#         user=user,
#         gym=gym,
#         role__in=[
#             GymMembership.Role.OWNER,
#             GymMembership.Role.MANAGER,
#             GymMembership.Role.STAFF,
#         ],
#         is_active=True,
#     ).exists()


# def is_gym_owner(user, gym):
#     """
#     Return True if the user is an active Owner
#     of the given gym.

#     Allowed:
#         - Superuser
#         - Owner

#     Not allowed:
#         - Manager
#         - Staff
#         - Trainer
#         - Member
#         - Unauthenticated users
#     """

#     if not user.is_authenticated:
#         return False

#     if user.is_superuser:
#         return True

#     return GymMembership.objects.filter(
#         user=user,
#         gym=gym,
#         role=GymMembership.Role.OWNER,
#         is_active=True,
#     ).exists()


# # ============================================================
# # Gym Permissions
# # ============================================================

# class CanViewGym(BasePermission):
#     """
#     Permission for viewing Gym.

#     GET is public.

#     Allowed:
#         - Authenticated users
#         - Unauthenticated users
#     """

#     def has_permission(self, request, view):
#         return True


# class CanCreateGym(BasePermission):
#     """
#     Permission for creating a Gym.

#     Allowed:
#         - Superuser only
#     """

#     message = (
#         "Only administrators can create a gym."
#     )

#     def has_permission(self, request, view):
#         return (
#             request.user.is_authenticated
#             and request.user.is_superuser
#         )


# class CanManageGym(BasePermission):
#     """
#     Permission for updating or deleting a Gym.

#     Used for:

#         PUT    /api/gyms/gym/{id}/
#         PATCH  /api/gyms/gym/{id}/
#         DELETE /api/gyms/gym/{id}/

#     Allowed:
#         - Superuser
#         - Owner
#         - Manager

#     Not allowed:
#         - Staff
#         - Trainer
#         - Member
#         - Unauthenticated users
#     """

#     message = (
#         "You do not have permission to manage this gym."
#     )

#     def has_object_permission(
#         self,
#         request,
#         view,
#         obj,
#     ):
#         return is_gym_owner_or_manager(
#             request.user,
#             obj,
#         )


# class CanAddStaff(BasePermission):
#     """
#     Permission for adding a Staff member or Trainer
#     to a Gym.

#     Used for:

#         POST /api/gyms/gym/{gym_id}/add_staff/

#     Allowed:
#         - Superuser
#         - Owner
#         - Manager

#     Not allowed:
#         - Staff
#         - Trainer
#         - Member

#     The exact role hierarchy is checked inside
#     the Service layer.
#     """

#     message = (
#         "You do not have permission to add "
#         "a member to this gym."
#     )

#     def has_permission(self, request, view):
#         gym = get_gym_from_url(view)

#         return is_gym_owner_or_manager(
#             request.user,
#             gym,
#         )


# class CanViewGymMembers(BasePermission):
#     """
#     Permission for viewing Gym members.

#     Used for:

#         GET /api/gyms/gym/{gym_id}/members/

#     Allowed:
#         - Superuser
#         - Owner
#         - Manager
#         - Staff

#     Not allowed:
#         - Trainer
#         - Member
#         - Unauthenticated users
#     """

#     message = (
#         "You do not have permission to view "
#         "members of this gym."
#     )

#     def has_permission(self, request, view):
#         gym = get_gym_from_url(view)

#         return is_gym_staff(
#             request.user,
#             gym,
#         )


# # ============================================================
# # GymMembership Permissions
# # ============================================================

# class CanViewGymMembership(BasePermission):
#     """
#     Permission for viewing GymMembership records.

#     Used for:

#         GET /api/gyms/{gym_id}/gymmembership/
#         GET /api/gyms/{gym_id}/gymmembership/{id}/

#     Allowed:
#         - Superuser
#         - Owner
#         - Manager

#     Not allowed:
#         - Staff
#         - Trainer
#         - Member
#         - Unauthenticated users
#     """

#     message = (
#         "You do not have permission to view "
#         "memberships of this gym."
#     )

#     def has_permission(self, request, view):
#         gym = get_gym_from_url(view)

#         return is_gym_owner_or_manager(
#             request.user,
#             gym,
#         )


# class CanCreateGymMembership(BasePermission):
#     """
#     Permission for creating a GymMembership.

#     Used for:

#         POST /api/gyms/{gym_id}/gymmembership/

#     Allowed:
#         - Superuser
#         - Owner
#         - Manager

#     Not allowed:
#         - Staff
#         - Trainer
#         - Member
#         - Unauthenticated users

#     The exact role hierarchy is handled
#     by the Service layer.
#     """

#     message = (
#         "You do not have permission to create "
#         "a membership in this gym."
#     )

#     def has_permission(self, request, view):
#         gym = get_gym_from_url(view)

#         return is_gym_owner_or_manager(
#             request.user,
#             gym,
#         )


# class CanManageGymMembership(BasePermission):
#     """
#     Permission for managing an existing GymMembership.

#     Used for:

#         GET    /api/gyms/{gym_id}/gymmembership/{id}/
#         PUT    /api/gyms/{gym_id}/gymmembership/{id}/
#         PATCH  /api/gyms/{gym_id}/gymmembership/{id}/
#         DELETE /api/gyms/{gym_id}/gymmembership/{id}/

#         PATCH /api/gyms/{gym_id}/gymmembership/{id}/update_membership/
#         POST  /api/gyms/{gym_id}/gymmembership/{id}/deactivate/

#     Allowed:
#         - Superuser
#         - Owner

#     Not allowed:
#         - Manager
#         - Staff
#         - Trainer
#         - Member
#         - Unauthenticated users
#     """

#     message = (
#         "Only the gym owner or administrator "
#         "can manage this membership."
#     )

#     def has_permission(self, request, view):
#         gym = get_gym_from_url(view)

#         return is_gym_owner(
#             request.user,
#             gym,
#         )

 

from django.shortcuts import get_object_or_404

from rest_framework.permissions import BasePermission

from gyms.models import Gym, GymMembership


# ============================================================
# Helper Functions
# ============================================================

def get_gym_from_url(view):
    """
    Get the Gym object from gym_id in the URL.

    Example:
        /api/gyms/{gym_id}/gymmembership/
    """

    gym_id = view.kwargs.get("gym_id")

    return get_object_or_404(
        Gym,
        pk=gym_id,
    )


def is_gym_owner_or_manager(user, gym):
    """
    Check whether user is an active Owner or Manager
    of the given gym.

    Allowed:
        - Superuser
        - Owner
        - Manager
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return GymMembership.objects.filter(
        user=user,
        gym=gym,
        role__in=[
            GymMembership.Role.OWNER,
            GymMembership.Role.MANAGER,
        ],
        is_active=True,
    ).exists()


def is_gym_staff(user, gym):
    """
    Check whether user is an active Owner, Manager,
    or Staff member of the given gym.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return GymMembership.objects.filter(
        user=user,
        gym=gym,
        role__in=[
            GymMembership.Role.OWNER,
            GymMembership.Role.MANAGER,
            GymMembership.Role.STAFF,
        ],
        is_active=True,
    ).exists()


def is_gym_owner(user, gym):
    """
    Check whether user is an active Owner
    of the given gym.

    Allowed:
        - Superuser
        - Owner
    """

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return GymMembership.objects.filter(
        user=user,
        gym=gym,
        role=GymMembership.Role.OWNER,
        is_active=True,
    ).exists()


# ============================================================
# Gym Permissions
# ============================================================

class CanViewGym(BasePermission):
    """
    Public permission for viewing gyms.
    """

    def has_permission(self, request, view):
        return True


class CanCreateGym(BasePermission):
    """
    Only Superuser can create a gym.
    """

    message = "Only administrators can create a gym."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_superuser
        )


class CanManageGym(BasePermission):
    """
    Permission for updating or deleting a Gym.

    Allowed:
        - Superuser
        - Owner
        - Manager
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
        return is_gym_owner_or_manager(
            request.user,
            obj,
        )


class CanAddStaff(BasePermission):
    """
    Permission for adding a membership.

    Allowed:
        - Superuser
        - Owner
        - Manager

    Exact role hierarchy is checked in Service.
    """

    message = (
        "You do not have permission to add "
        "a member to this gym."
    )

    def has_permission(self, request, view):
        gym = get_gym_from_url(view)

        return is_gym_owner_or_manager(
            request.user,
            gym,
        )


class CanViewGymMembers(BasePermission):
    """
    Permission for viewing gym staff.

    Allowed:
        - Superuser
        - Owner
        - Manager
        - Staff
    """

    message = (
        "You do not have permission to view "
        "members of this gym."
    )

    def has_permission(self, request, view):
        gym = get_gym_from_url(view)

        return is_gym_staff(
            request.user,
            gym,
        )


# ============================================================
# GymMembership Permissions
# ============================================================

class CanViewGymMembership(BasePermission):
    """
    Permission for viewing GymMembership records.

    Allowed:
        - Superuser
        - Owner
        - Manager
    """

    message = (
        "You do not have permission to view "
        "memberships of this gym."
    )

    def has_permission(self, request, view):
        gym = get_gym_from_url(view)

        return is_gym_owner_or_manager(
            request.user,
            gym,
        )


class CanCreateGymMembership(BasePermission):
    """
    Permission for creating GymMembership.

    Allowed:
        - Superuser
        - Owner
        - Manager

    Exact role hierarchy is checked in Service.
    """

    message = (
        "You do not have permission to create "
        "a membership in this gym."
    )

    def has_permission(self, request, view):
        gym = get_gym_from_url(view)

        return is_gym_owner_or_manager(
            request.user,
            gym,
        )


class CanManageGymMembership(BasePermission):
    """
    Permission for managing an existing GymMembership.

    Used for:

        update_membership
        deactivate
        activate

    Allowed:
        - Superuser
        - Owner
        - Manager

    The exact target-role hierarchy is checked
    inside the Service layer.
    """

    message = (
        "You do not have permission to manage "
        "this membership."
    )

    def has_permission(self, request, view):
        gym = get_gym_from_url(view)

        return is_gym_owner_or_manager(
            request.user,
            gym,
        )

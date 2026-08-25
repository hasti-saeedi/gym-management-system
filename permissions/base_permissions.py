# from gyms.models import GymMembership


# # فقط برای سریالایزر کریت اینرولمنت ه بفهمه نقشش چیه 
# def is_gym_employee(user):
#     """
#     Return True if user has an active
#     Owner, Manager, or Staff role in any gym.
#     """

#     if not user.is_authenticated:
#         return False

#     return GymMembership.objects.filter(
#         user=user,
#         role__in=[
#             GymMembership.Role.OWNER,
#             GymMembership.Role.MANAGER,
#             GymMembership.Role.STAFF,
#         ],
#         is_active=True,
#     ).exists()

from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from gyms.models import Gym
from rest_framework.permissions import BasePermission


class IsAnonymous(BasePermission):
    """
    Allows access only to unauthenticated users.
    """

    def has_permission(self, request, view):
        return not request.user.is_authenticated

class AuthenticatedPermission(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated


class GymPermission(BasePermission):
    """
    Base permission for APIs that receive gym_id
    in the URL.
    """

    def get_gym(self, view):
        gym_id = view.kwargs.get("gym_id")

        return get_object_or_404(
            Gym,
            pk=gym_id,
        )

    def is_superuser(self, request):
        return (
            request.user.is_authenticated
            and request.user.is_superuser
        )
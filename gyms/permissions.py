from rest_framework.permissions import BasePermission
from gyms.models import GymMembership


class CanManageGymStaff(BasePermission):

    message = "You do not have permission to manage this gym staff."

    def has_object_permission(self, request, view, obj):

        if request.user.is_superuser:
            return True

        return GymMembership.objects.filter(
            user=request.user,
            gym=obj,
            role__in=[
                GymMembership.Role.OWNER,
                GymMembership.Role.MANAGER,
            ],
            is_active=True,
        ).exists()
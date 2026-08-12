from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from gyms.models import Gym, GymMembership


def get_staff_statistics(gym_id):

    gym = get_object_or_404(
        Gym,
        pk=gym_id,
    )

    statistics = GymMembership.objects.filter(
        gym=gym,
        role__in=[
            GymMembership.Role.OWNER,
            GymMembership.Role.MANAGER,
            GymMembership.Role.STAFF,
        ],
    ).aggregate(

        owners=Count(
            "id",
            filter=Q(role=GymMembership.Role.OWNER),
        ),

        managers=Count(
            "id",
            filter=Q(role=GymMembership.Role.MANAGER),
        ),

        staff=Count(
            "id",
            filter=Q(role=GymMembership.Role.STAFF),
        ),

        active=Count(
            "id",
            filter=Q(is_active=True),
        ),

        inactive=Count(
            "id",
            filter=Q(is_active=False),
        ),

        total=Count("id"),
    )

    return statistics
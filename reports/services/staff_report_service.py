from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from gyms.models import Gym, GymMembership


def get_staff_statistics(gym_id):
    """
    Return staff statistics for a specific gym.

    The statistics include the number of owners, managers,
    staff members, and the total number of active and inactive
    staff members.
    """

    gym = get_object_or_404(
        Gym,
        pk=gym_id,
    )

    return (
        GymMembership.objects.filter(
            gym=gym,
            role__in=[
                GymMembership.Role.OWNER,
                GymMembership.Role.MANAGER,
                GymMembership.Role.STAFF,
            ],
        )
        .aggregate(
            owners=Count(
                "id",
                filter=Q(
                    role=GymMembership.Role.OWNER,
                ),
            ),
            managers=Count(
                "id",
                filter=Q(
                    role=GymMembership.Role.MANAGER,
                ),
            ),
            staff=Count(
                "id",
                filter=Q(
                    role=GymMembership.Role.STAFF,
                ),
            ),
            active=Count(
                "id",
                filter=Q(
                    is_active=True,
                ),
            ),
            inactive=Count(
                "id",
                filter=Q(
                    is_active=False,
                ),
            ),
            total=Count("id"),
        )
    )
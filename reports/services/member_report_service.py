from django.db.models import Count
from django.db.models.functions import ExtractMonth
from django.shortcuts import get_object_or_404

from gyms.models import Gym, GymMembership


def get_member_statistics(gym_id):
    """
    Return member statistics for a specific gym.

    The statistics include the total number of members
    and the number of active and inactive members.
    """

    gym = get_object_or_404(
        Gym,
        pk=gym_id,
    )

    queryset = GymMembership.objects.filter(
        gym=gym,
        role=GymMembership.Role.MEMBER,
    )

    return {
        "total": queryset.count(),
        "active": queryset.filter(
            is_active=True,
        ).count(),
        "inactive": queryset.filter(
            is_active=False,
        ).count(),
    }


def get_new_members(gym_id):
    """
    Return the ten most recently joined members of a gym.

    Members are ordered by their joining date in descending order.
    """

    gym = get_object_or_404(
        Gym,
        pk=gym_id,
    )

    return (
        GymMembership.objects.filter(
            gym=gym,
            role=GymMembership.Role.MEMBER,
        )
        .order_by("-joined_at")[:10]
    )


def get_members_by_month(gym_id):
    """
    Return the number of new members grouped by month.

    The result contains the month number and the number
    of members who joined during that month.
    """

    gym = get_object_or_404(
        Gym,
        pk=gym_id,
    )

    return (
        GymMembership.objects.filter(
            gym=gym,
            role=GymMembership.Role.MEMBER,
        )
        .annotate(
            month=ExtractMonth("joined_at"),
        )
        .values("month")
        .annotate(
            total=Count("id"),
        )
        .order_by("month")
    )
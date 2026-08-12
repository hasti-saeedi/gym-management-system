from django.db.models import Count
from gyms.models import GymMembership
from django.shortcuts import get_object_or_404
from gyms.models import Gym
from gyms.models import Gym, GymMembership
from django.db.models.functions import ExtractMonth



def get_member_statistics(gym_id):

    gym = get_object_or_404(
        Gym,
        pk=gym_id,
    )
    queryset = GymMembership.objects.filter(
        gym_id=gym,
        role="member",
    )

    total = queryset.count()

    active = queryset.filter(
        is_active=True,
    ).count()

    inactive = queryset.filter(
        is_active=False,
    ).count()

    return {
        "total": total,
        "active": active,
        "inactive": inactive,
    }


def get_new_members(gym_id):

    gym = get_object_or_404(
        Gym,
        pk=gym_id,
    )

    queryset = GymMembership.objects.filter(
        gym_id=gym,
        role="member",
    ).order_by("-joined_at")[:10]

    return queryset

def get_members_by_month(gym_id):

    gym = get_object_or_404(
        Gym,
        pk=gym_id,
    )

    queryset = (
        GymMembership.objects.filter(
            gym=gym,
            role="member",
        )
        .annotate(
            month=ExtractMonth("joined_at")
        )
        .values("month")
        .annotate(
            total=Count("id")
        )
        .order_by("month")
    )

    return queryset
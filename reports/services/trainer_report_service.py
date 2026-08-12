from django.db.models import Count
from django.shortcuts import get_object_or_404

from gyms.models import Gym, GymMembership
from classes.models import GymClass


def get_trainers_workload(gym_id):

    gym = get_object_or_404(
        Gym,
        pk=gym_id,
    )

    queryset = (
        GymMembership.objects.filter(
            gym=gym,
            role=GymMembership.Role.TRAINER,
        )
        .select_related("user")
        .annotate(
            total_classes=Count(
                "user__taught_classes",
                distinct=True,
            ),
        )
    )

    return queryset
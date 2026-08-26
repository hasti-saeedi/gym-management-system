from django.db.models import Count
from django.shortcuts import get_object_or_404

from gyms.models import Gym, GymMembership


def get_trainers_workload(gym_id):
    """
    Return the workload of trainers in a specific gym.

    Each trainer membership is annotated with the total number
    of classes taught by the associated user.
    """

    gym = get_object_or_404(
        Gym,
        pk=gym_id,
    )

    return (
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
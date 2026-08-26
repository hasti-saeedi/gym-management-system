from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404

from classes.models import GymClass
from gyms.models import Gym


def get_class_statistics(gym_id):
    """Return class statistics for a gym."""

    gym = get_object_or_404(
        Gym,
        pk=gym_id,
    )

    return GymClass.objects.filter(
        gym=gym,
    ).aggregate(
        total=Count("id"),
        active=Count(
            "id",
            filter=Q(is_active=True),
        ),
        inactive=Count(
            "id",
            filter=Q(is_active=False),
        ),
        full=Count(
            "id",
            filter=Q(
                current_enrolled__gte=F("capacity"),
            ),
        ),
        available=Count(
            "id",
            filter=Q(
                current_enrolled__lt=F("capacity"),
            ),
        ),
    )
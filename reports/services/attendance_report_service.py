from django.shortcuts import get_object_or_404
from django.utils import timezone

from classes.models import ClassSession
from gyms.models import Gym


def get_attendance_statistics(gym_id):
    """Return attendance statistics for sessions belonging to a gym."""

    get_object_or_404(
        Gym,
        pk=gym_id,
    )

    queryset = ClassSession.objects.filter(
        gym_class__gym_id=gym_id,
    )

    total_sessions = queryset.count()

    cancelled_sessions = queryset.filter(
        is_cancelled=True,
    ).count()

    active_sessions = queryset.filter(
        is_cancelled=False,
    ).count()

    return {
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "cancelled_sessions": cancelled_sessions,
    }


def get_today_sessions(gym_id):
    """Return today's sessions for a gym ordered by start time."""

    get_object_or_404(
        Gym,
        pk=gym_id,
    )

    today = timezone.localdate()

    return (
        ClassSession.objects
        .filter(
            gym_class__gym_id=gym_id,
            start_time__date=today,
        )
        .order_by("start_time")
    )


def get_cancelled_sessions(gym_id):
    """Return cancelled sessions for a gym ordered by most recent first."""

    get_object_or_404(
        Gym,
        pk=gym_id,
    )

    return (
        ClassSession.objects
        .filter(
            gym_class__gym_id=gym_id,
            is_cancelled=True,
        )
        .order_by("-start_time")
    )
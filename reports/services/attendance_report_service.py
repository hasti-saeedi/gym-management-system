from django.db.models import Count
from classes.models import ClassSession
from django.utils import timezone
from django.shortcuts import get_object_or_404
from gyms.models import Gym


def get_attendance_statistics(gym_id):

    gym = get_object_or_404(
    Gym,
    pk=gym_id,
)
    queryset = ClassSession.objects.filter(
        gym_class__gym_id=gym
    )

    total_sessions = queryset.count()

    cancelled_sessions = queryset.filter(
        is_cancelled=True
    ).count()

    active_sessions = queryset.filter(
        is_cancelled=False
    ).count()

    return {
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "cancelled_sessions": cancelled_sessions,
    }

def get_today_sessions(gym_id):

    gym = get_object_or_404(
    Gym,
    pk=gym_id,
)

    today = timezone.localdate()

    queryset = ClassSession.objects.filter(
        gym_class__gym_id=gym,
        start_time__date=today,
    ).order_by("start_time")

    return queryset

def get_cancelled_sessions(gym_id):

    gym = get_object_or_404(
    Gym,
    pk=gym_id,
)
    queryset = ClassSession.objects.filter(
        gym_class__gym_id=gym,
        is_cancelled=True,
    ).order_by("-start_time")

    return queryset
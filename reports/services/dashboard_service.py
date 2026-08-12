from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from gyms.models import Gym, GymMembership
from classes.models import GymClass, ClassSession

def get_member_statistics(gym_id):
    return (
        GymMembership.objects.filter(
            gym_id=gym_id,
            role=GymMembership.Role.MEMBER,
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
        )
    )

def get_staff_statistics(gym_id):
    return (
        GymMembership.objects.filter(
            gym_id=gym_id,
        )
        .exclude(role=GymMembership.Role.MEMBER)
        .aggregate(
            total=Count("id"),
            active=Count("id", filter=Q(is_active=True)),
            inactive=Count("id", filter=Q(is_active=False)),
            owners=Count("id", filter=Q(role=GymMembership.Role.OWNER)),
            managers=Count("id", filter=Q(role=GymMembership.Role.MANAGER)),
            trainers=Count("id", filter=Q(role=GymMembership.Role.TRAINER)),
            staff=Count("id", filter=Q(role=GymMembership.Role.STAFF)),
        )
    )

def get_class_statistics(gym_id):
    return (
        GymClass.objects.filter(
            gym_id=gym_id,
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
        )
    )

def get_session_statistics(gym_id):

    now = timezone.now()
    today = timezone.localdate()

    return (
        ClassSession.objects.filter(
            gym_class__gym_id=gym_id,
        ).aggregate(

            total=Count("id"),

            today=Count(
                "id",
                filter=Q(start_time__date=today),
            ),

            cancelled=Count(
                "id",
                filter=Q(is_cancelled=True),
            ),

            running=Count(
                "id",
                filter=Q(
                    start_time__lte=now,
                    end_time__gte=now,
                    is_cancelled=False,
                ),
            ),

            finished=Count(
                "id",
                filter=Q(
                    end_time__lt=now,
                    is_cancelled=False,
                ),
            ),

            upcoming=Count(
                "id",
                filter=Q(
                    start_time__gt=now,
                    is_cancelled=False,
                ),
            ),
        )
    )

def get_gym_info(gym_id):

    gym = get_object_or_404(
        Gym,
        pk=gym_id,
    )

    return {
        "id": gym.id,
        "name": gym.name,
        "is_active": gym.is_active,
    }

def get_dashboard(gym_id):

    return {
        "gym": get_gym_info(gym_id),
        "members": get_member_statistics(gym_id),
        "staff": get_staff_statistics(gym_id),
        "classes": get_class_statistics(gym_id),
        "sessions": get_session_statistics(gym_id),
    }
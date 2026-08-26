"""
Serializers for gym dashboard and statistical reports.
"""

from rest_framework import serializers


class GymInfoReportSerializer(serializers.Serializer):
    """Serialize basic gym information for reports."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    is_active = serializers.BooleanField()


class MemberStatisticsReportSerializer(serializers.Serializer):
    """Serialize member statistics for reports."""

    total = serializers.IntegerField()
    active = serializers.IntegerField()
    inactive = serializers.IntegerField()


class StaffStatisticsReportSerializer(serializers.Serializer):
    """Serialize staff statistics and role distribution."""

    total = serializers.IntegerField()
    active = serializers.IntegerField()
    inactive = serializers.IntegerField()
    owners = serializers.IntegerField()
    managers = serializers.IntegerField()
    trainers = serializers.IntegerField()
    staff = serializers.IntegerField()


class ClassStatisticsReportSerializer(serializers.Serializer):
    """Serialize class statistics for reports."""

    total = serializers.IntegerField()
    active = serializers.IntegerField()
    inactive = serializers.IntegerField()


class SessionStatisticsReportSerializer(serializers.Serializer):
    """Serialize session statistics for reports."""

    total = serializers.IntegerField()
    today = serializers.IntegerField()
    cancelled = serializers.IntegerField()
    running = serializers.IntegerField()
    finished = serializers.IntegerField()
    upcoming = serializers.IntegerField()


class DashboardReportSerializer(serializers.Serializer):
    """Serialize the complete gym dashboard report."""

    gym = GymInfoReportSerializer()
    members = MemberStatisticsReportSerializer()
    staff = StaffStatisticsReportSerializer()
    classes = ClassStatisticsReportSerializer()
    sessions = SessionStatisticsReportSerializer()


class MemberStatisticsSerializer(serializers.Serializer):
    """Serialize basic member statistics."""

    total = serializers.IntegerField()
    active = serializers.IntegerField()
    inactive = serializers.IntegerField()


class NewMemberReportSerializer(serializers.Serializer):
    """Serialize information about a newly joined member."""

    id = serializers.IntegerField(
        source="user.id",
    )

    username = serializers.CharField(
        source="user.username",
    )

    joined_at = serializers.DateTimeField()


class MemberMonthlyReportSerializer(serializers.Serializer):
    """Serialize monthly member statistics."""

    month = serializers.IntegerField()
    total = serializers.IntegerField()


class AttendanceStatisticsReportSerializer(serializers.Serializer):
    """Serialize attendance-related session statistics."""

    total_sessions = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    cancelled_sessions = serializers.IntegerField()


class SessionReportSerializer(serializers.Serializer):
    """Serialize session information for reports."""

    id = serializers.IntegerField()

    class_name = serializers.CharField(
        source="gym_class.name",
    )

    trainer = serializers.CharField(
        source="trainer.username",
        allow_null=True,
    )

    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    is_cancelled = serializers.BooleanField()


class TrainerWorkloadReportSerializer(serializers.Serializer):
    """Serialize trainer workload statistics."""

    trainer_id = serializers.IntegerField(
        source="user.id",
    )

    trainer_name = serializers.CharField(
        source="user.username",
    )

    total_classes = serializers.IntegerField()


class ClassStatisticsReportSerializer(serializers.Serializer):
    """Serialize detailed class statistics."""

    total = serializers.IntegerField()
    active = serializers.IntegerField()
    inactive = serializers.IntegerField()
    full = serializers.IntegerField()
    available = serializers.IntegerField()
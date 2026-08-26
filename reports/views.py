from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.serializers import (
    AttendanceStatisticsReportSerializer,
    ClassStatisticsReportSerializer,
    DashboardReportSerializer,
    MemberMonthlyReportSerializer,
    MemberStatisticsReportSerializer,
    NewMemberReportSerializer,
    SessionReportSerializer,
    StaffStatisticsReportSerializer,
    TrainerWorkloadReportSerializer,
)

from reports.services.attendance_report_service import (
    get_attendance_statistics,
    get_cancelled_sessions,
    get_today_sessions,
)
from reports.services.class_report_service import get_class_statistics
from reports.services.dashboard_service import get_dashboard
from reports.services.member_report_service import (
    get_member_statistics,
    get_members_by_month,
    get_new_members,
)
from reports.services.staff_report_service import get_staff_statistics
from reports.services.trainer_report_service import get_trainers_workload


@extend_schema(
    responses=DashboardReportSerializer,
)
class DashboardAPIView(APIView):
    """Return a complete dashboard report for a gym."""

    def get(self, request, gym_id):
        data = get_dashboard(gym_id)

        serializer = DashboardReportSerializer(
            instance=data,
        )

        return Response(serializer.data)


@extend_schema(
    responses=MemberStatisticsReportSerializer,
)
class MemberStatisticsAPIView(APIView):
    """Return member statistics for a gym."""

    def get(self, request, gym_id):
        data = get_member_statistics(gym_id)

        serializer = MemberStatisticsReportSerializer(
            instance=data,
        )

        return Response(serializer.data)


@extend_schema(
    responses=NewMemberReportSerializer(many=True),
)
class NewMemberAPIView(APIView):
    """Return recently joined members of a gym."""

    def get(self, request, gym_id):
        queryset = get_new_members(gym_id)

        serializer = NewMemberReportSerializer(
            instance=queryset,
            many=True,
        )

        return Response(serializer.data)


@extend_schema(
    responses=MemberMonthlyReportSerializer(many=True),
)
class MemberMonthlyAPIView(APIView):
    """Return the number of new members grouped by month."""

    def get(self, request, gym_id):
        data = get_members_by_month(gym_id)

        serializer = MemberMonthlyReportSerializer(
            instance=data,
            many=True,
        )

        return Response(serializer.data)


@extend_schema(
    responses=AttendanceStatisticsReportSerializer,
)
class AttendanceStatisticsAPIView(APIView):
    """Return attendance statistics for a gym."""

    def get(self, request, gym_id):
        data = get_attendance_statistics(gym_id)

        serializer = AttendanceStatisticsReportSerializer(
            instance=data,
        )

        return Response(serializer.data)


@extend_schema(
    responses=SessionReportSerializer(many=True),
)
class TodaySessionsAPIView(APIView):
    """Return today's sessions for a gym."""

    def get(self, request, gym_id):
        queryset = get_today_sessions(gym_id)

        serializer = SessionReportSerializer(
            instance=queryset,
            many=True,
        )

        return Response(serializer.data)


@extend_schema(
    responses=SessionReportSerializer(many=True),
)
class CancelledSessionsAPIView(APIView):
    """Return cancelled sessions for a gym."""

    def get(self, request, gym_id):
        queryset = get_cancelled_sessions(gym_id)

        serializer = SessionReportSerializer(
            instance=queryset,
            many=True,
        )

        return Response(serializer.data)


@extend_schema(
    responses=StaffStatisticsReportSerializer,
)
class StaffStatisticsAPIView(APIView):
    """Return staff statistics for a gym."""

    def get(self, request, gym_id):
        data = get_staff_statistics(gym_id)

        serializer = StaffStatisticsReportSerializer(
            instance=data,
        )

        return Response(serializer.data)


@extend_schema(
    responses=TrainerWorkloadReportSerializer(many=True),
)
class TrainerWorkloadAPIView(APIView):
    """Return workload statistics for trainers in a gym."""

    def get(self, request, gym_id):
        data = get_trainers_workload(gym_id)

        serializer = TrainerWorkloadReportSerializer(
            instance=data,
            many=True,
        )

        return Response(serializer.data)


@extend_schema(
    responses=ClassStatisticsReportSerializer,
)
class ClassStatisticsAPIView(APIView):
    """Return class statistics for a gym."""

    def get(self, request, gym_id):
        data = get_class_statistics(gym_id)

        serializer = ClassStatisticsReportSerializer(
            instance=data,
        )

        return Response(serializer.data)
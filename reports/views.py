from django.shortcuts import render

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from reports.services.dashboard_service import get_dashboard

from reports.serializers import DashboardReportSerializer

from reports.serializers import (
    MemberStatisticsReportSerializer,
    NewMemberReportSerializer,
    MemberMonthlyReportSerializer,
    ClassStatisticsReportSerializer,
    AttendanceStatisticsReportSerializer,
    SessionReportSerializer,
    StaffStatisticsReportSerializer
)

from reports.services.staff_report_service import (
    get_staff_statistics,
)

from reports.services.attendance_report_service import (
    get_attendance_statistics,
    get_today_sessions,
    get_cancelled_sessions,
)

from reports.services.member_report_service import (
    get_member_statistics,
    get_new_members,
    get_members_by_month,
)

from reports.services.class_report_service import get_class_statistics

@extend_schema(
    responses=DashboardReportSerializer,
)
class DashboardAPIView(APIView):

    def get(self, request, gym_id):

        data = get_dashboard(gym_id)

            #instance= یعنی دارم داده‌ای که از قبل دارم را نمایش می‌دهم.
        serializer = DashboardReportSerializer(instance=data)  

        return Response(serializer.data)


############# member
@extend_schema(
    responses=MemberStatisticsReportSerializer,
)
class MemberStatisticsAPIView(APIView):

    def get(self, request, gym_id):

        data = get_member_statistics(gym_id)

        serializer = MemberStatisticsReportSerializer(
            instance=data
        )

        return Response(serializer.data)
    
@extend_schema(
    responses=NewMemberReportSerializer(many=True),
)
class NewMemberAPIView(APIView):

    def get(self, request, gym_id):

        queryset = get_new_members(gym_id)

        serializer =NewMemberReportSerializer(
            instance=queryset,
            many=True,#این یک لیست از آبجکت‌هاست.
        )

        return Response(serializer.data)

@extend_schema(
    responses=MemberMonthlyReportSerializer(many=True),
)
class MemberMonthlyAPIView(APIView):

    def get(self, request, gym_id):

        data = get_members_by_month(gym_id)

        serializer = MemberMonthlyReportSerializer(
            instance=data,
            many=True,
        )

        return Response(serializer.data)

##### attendance
    
@extend_schema(
    responses=AttendanceStatisticsReportSerializer,
)
class AttendanceStatisticsAPIView(APIView):

    def get(self, request, gym_id):

        data = get_attendance_statistics(gym_id)

        serializer = AttendanceStatisticsReportSerializer(
            instance=data
        )

        return Response(serializer.data)
    

@extend_schema(
    responses=SessionReportSerializer(many=True),
)
class TodaySessionsAPIView(APIView):

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

    def get(self, request, gym_id):

        queryset = get_cancelled_sessions(gym_id)

        serializer =SessionReportSerializer(
            instance=queryset,
            many=True,
        )

        return Response(serializer.data)
    
#### staff
    
@extend_schema(
    responses=StaffStatisticsReportSerializer,
)
class StaffStatisticsAPIView(APIView):

    def get(self, request, gym_id):

        data = get_staff_statistics(gym_id)

        serializer = StaffStatisticsReportSerializer(
            instance=data,
        )

        return Response(serializer.data)

#### trainer
from reports.services.trainer_report_service import (
    get_trainers_workload,
)
from reports.serializers import (
    TrainerWorkloadReportSerializer,
)
@extend_schema(
    responses=TrainerWorkloadReportSerializer(many=True),
)
class TrainerWorkloadAPIView(APIView):

    def get(self, request, gym_id):

        data = get_trainers_workload(gym_id)

        serializer = TrainerWorkloadReportSerializer(
            instance=data,
            many=True,
        )

        return Response(serializer.data)
    
### class
@extend_schema(
    responses=ClassStatisticsReportSerializer,
)
class ClassStatisticsAPIView(APIView):

    def get(self, request, gym_id):

        data = get_class_statistics(gym_id)

        serializer = ClassStatisticsReportSerializer(
            instance=data,
        )

        return Response(serializer.data)
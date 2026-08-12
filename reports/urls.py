from django.urls import path

from reports.views import (
    DashboardAPIView,
    MemberStatisticsAPIView,
    NewMemberAPIView,
    MemberMonthlyAPIView,
    AttendanceStatisticsAPIView,
    TodaySessionsAPIView,
    CancelledSessionsAPIView,
    StaffStatisticsAPIView,
    TrainerWorkloadAPIView,
    ClassStatisticsAPIView

)

urlpatterns = [
### dashboard
    path(
        "dashboard/<int:gym_id>/",
        DashboardAPIView.as_view(),
        name="dashboard",
    ),

### member
    path(
        "members/statistics/<int:gym_id>/",
        MemberStatisticsAPIView.as_view(),
    ),

    path(
        "members/new/<int:gym_id>/",
        NewMemberAPIView.as_view(),
    ),

    path(
        "members/monthly/<int:gym_id>/",
        MemberMonthlyAPIView.as_view(),
    ),

###  attendance
    path(
        "attendance/statistics/<int:gym_id>/",
        AttendanceStatisticsAPIView.as_view(),
    ),

    path(
        "attendance/today/<int:gym_id>/",
        TodaySessionsAPIView.as_view(),
    ),

    path(
        "attendance/cancelled/<int:gym_id>/",
        CancelledSessionsAPIView.as_view(),
    ),

### staff
    path(
        "staff/statistics/<int:gym_id>/",
        StaffStatisticsAPIView.as_view(),
        name="staff-statistics",
    ),

### trainer
    path(
        "trainers/workload/<int:gym_id>/",
        TrainerWorkloadAPIView.as_view(),
    ),

### class
    path(
        "classes/statistics/<int:gym_id>/",
        ClassStatisticsAPIView.as_view(),
        name="class-statistics",
    ),
]
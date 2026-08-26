from django.urls import path

from reports.views import (
    AttendanceStatisticsAPIView,
    CancelledSessionsAPIView,
    ClassStatisticsAPIView,
    DashboardAPIView,
    MemberMonthlyAPIView,
    MemberStatisticsAPIView,
    NewMemberAPIView,
    StaffStatisticsAPIView,
    TodaySessionsAPIView,
    TrainerWorkloadAPIView,
)


urlpatterns = [
    path(
        "dashboard/<int:gym_id>/",
        DashboardAPIView.as_view(),
        name="dashboard",
    ),

    path(
        "members/statistics/<int:gym_id>/",
        MemberStatisticsAPIView.as_view(),
        name="member-statistics",
    ),

    path(
        "members/new/<int:gym_id>/",
        NewMemberAPIView.as_view(),
        name="new-members",
    ),

    path(
        "members/monthly/<int:gym_id>/",
        MemberMonthlyAPIView.as_view(),
        name="member-monthly",
    ),

    path(
        "attendance/statistics/<int:gym_id>/",
        AttendanceStatisticsAPIView.as_view(),
        name="attendance-statistics",
    ),

    path(
        "attendance/today/<int:gym_id>/",
        TodaySessionsAPIView.as_view(),
        name="today-sessions",
    ),

    path(
        "attendance/cancelled/<int:gym_id>/",
        CancelledSessionsAPIView.as_view(),
        name="cancelled-sessions",
    ),

    path(
        "staff/statistics/<int:gym_id>/",
        StaffStatisticsAPIView.as_view(),
        name="staff-statistics",
    ),

    path(
        "trainers/workload/<int:gym_id>/",
        TrainerWorkloadAPIView.as_view(),
        name="trainer-workload",
    ),

    path(
        "classes/statistics/<int:gym_id>/",
        ClassStatisticsAPIView.as_view(),
        name="class-statistics",
    ),
]
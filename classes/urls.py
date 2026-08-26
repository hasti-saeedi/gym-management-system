from django.urls import path

from .views import ClassSessionViewSet, GymClassViewSet


urlpatterns = [
    path(
        "classes/",
        GymClassViewSet.as_view({
            "get": "list",
        }),
        name="public-class-list",
    ),

    path(
        "classes/<int:pk>/",
        GymClassViewSet.as_view({
            "get": "retrieve",
        }),
        name="public-class-detail",
    ),

    path(
        "gyms/<int:gym_id>/classes/",
        GymClassViewSet.as_view({
            "get": "list",
            "post": "create",
        }),
        name="gym-class-list",
    ),

    path(
        "gyms/<int:gym_id>/classes/<int:pk>/",
        GymClassViewSet.as_view({
            "get": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy",
        }),
        name="gym-class-detail",
    ),

    path(
        "gyms/<int:gym_id>/classes/<int:class_id>/sessions/",
        ClassSessionViewSet.as_view({
            "get": "list",
            "post": "create",
        }),
        name="class-session-list",
    ),

    path(
        "gyms/<int:gym_id>/classes/<int:class_id>/sessions/<int:pk>/",
        ClassSessionViewSet.as_view({
            "get": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy",
        }),
        name="class-session-detail",
    ),

    path(
        "gyms/<int:gym_id>/classes/<int:class_id>/sessions/<int:pk>/get_students/",
        ClassSessionViewSet.as_view({
            "get": "get_students",
        }),
        name="session-students",
    ),

    path(
        "gyms/<int:gym_id>/classes/<int:class_id>/sessions/<int:pk>/record_attendance/",
        ClassSessionViewSet.as_view({
            "post": "record_attendance",
        }),
        name="record-attendance",
    ),
]
# from django.urls import path
# from .views import GymClassViewSet, ClassSessionViewSet


# urlpatterns = [

#     # Public classes
#     path(
#         "classes/",
#         GymClassViewSet.as_view({
#             "get": "list",
#         }),
#         name="public-class-list",
#     ),

#     path(
#         "classes/<int:pk>/",
#         GymClassViewSet.as_view({
#             "get": "retrieve",
#         }),
#         name="public-class-detail",
#     ),


#     # Gym management
#     path(
#         "gyms/<int:gym_id>/classes/",
#         GymClassViewSet.as_view({
#             "get": "list",
#             "post": "create",
#         }),
#         name="gym-class-list",
#     ),

#     path(
#         "gyms/<int:gym_id>/classes/<int:pk>/",
#         GymClassViewSet.as_view({
#             "get": "retrieve",
#             "put": "update",
#             "patch": "partial_update",
#             "delete": "destroy",
#         }),
#         name="gym-class-detail",
#     ),


# #classsessions
#     path(
#         "gyms/<int:gym_id>/classes/<int:class_id>/sessions/",
#         ClassSessionViewSet.as_view(
#             {
#                 "get": "list",
#                 "post": "create",
#             }
#         ),
#         name="class-sessions",
#     ),


#     path(
#         "gyms/<int:gym_id>/classes/<int:class_id>/sessions/<int:pk>/",
#         ClassSessionViewSet.as_view(
#             {
#                 "get": "retrieve",
#                 "put": "update",
#                 "patch": "partial_update",
#                 "delete": "destroy",
#             }
#         ),
#         name="class-session-detail",
#     ),


#     path(
#         "gyms/<int:gym_id>/classes/<int:class_id>/sessions/<int:pk>/get_students/",
#         ClassSessionViewSet.as_view(
#             {
#                 "get": "get_students",
#             }
#         ),
#         name="session-students",
#     ),


#     path(
#         "gyms/<int:gym_id>/classes/<int:class_id>/sessions/<int:pk>/record_attendance/",
#         ClassSessionViewSet.as_view(
#             {
#                 "post": "record_attendance",
#             }
#         ),
#         name="record-attendance",
#     ),


# ]

from django.urls import path
from .views import GymClassViewSet, ClassSessionViewSet


urlpatterns = [

    # =====================================
    # Public Classes
    # =====================================

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


    # =====================================
    # Gym Classes Management
    # =====================================

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


    # =====================================
    # Class Sessions List & Create
    # =====================================

    path(
        "gyms/<int:gym_id>/classes/<int:class_id>/sessions/",
        ClassSessionViewSet.as_view({
            "get": "list",
            "post": "create",
        }),
        name="class-session-list",
    ),


    # =====================================
    # Class Session Detail CRUD
    # =====================================

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


    # =====================================
    # Session Actions
    # =====================================

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


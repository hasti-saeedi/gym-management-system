from django.urls import path

from .views import (
    CurrentUserView,
    GymUserViewSet,
    LoginView,
    LogoutView,
    RegisterView,
)


urlpatterns = [
    # Authentication
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    # Current user
    path(
        "me/",
        CurrentUserView.as_view(),
        name="current-user",
    ),

    # Gym users
    path(
        "gyms/<int:gym_id>/users/",
        GymUserViewSet.as_view({
            "get": "list",
            "post": "create",
        }),
        name="gym-users",
    ),
    path(
        "gyms/<int:gym_id>/users/<int:pk>/",
        GymUserViewSet.as_view({
            "get": "retrieve",
            "put": "update",
            "patch": "partial_update",
            "delete": "destroy",
        }),
        name="gym-user-detail",
    ),
]
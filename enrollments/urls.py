from django.urls import path

from .views import EnrollmentViewSet, PaymentViewSet


urlpatterns = [
    path(
        "gyms/<int:gym_id>/enrollments/",
        EnrollmentViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="gym-enrollment-list",
    ),

    path(
        "enrollments/my/",
        EnrollmentViewSet.as_view(
            {
                "get": "my_enrollments",
            }
        ),
        name="my-enrollments",
    ),

    path(
        "gyms/<int:gym_id>/enrollments/<int:pk>/",
        EnrollmentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="enrollment-detail",
    ),

    path(
        "gyms/<int:gym_id>/enrollments/<int:pk>/cancel/",
        EnrollmentViewSet.as_view(
            {
                "post": "cancel",
            }
        ),
        name="enrollment-cancel",
    ),

    path(
        "gyms/<int:gym_id>/payments/",
        PaymentViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="payment-list",
    ),

    path(
        "payments/my/",
        PaymentViewSet.as_view(
            {
                "get": "my_payments",
            }
        ),
        name="my-payments",
    ),

    path(
        "gyms/<int:gym_id>/payments/<int:pk>/",
        PaymentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="payment-detail",
    ),

    path(
        "gyms/<int:gym_id>/payments/<int:pk>/confirm/",
        PaymentViewSet.as_view(
            {
                "post": "confirm",
            }
        ),
        name="payment-confirm",
    ),
]
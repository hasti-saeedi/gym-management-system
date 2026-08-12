# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import EnrollmentViewSet, PaymentViewSet

# router = DefaultRouter()
# router.register('enrollments', EnrollmentViewSet)

# router.register('payments', PaymentViewSet)
# urlpatterns =[
#     path('', include(router.urls)),
#     path(
#     "enrollments/<int:pk>/cancel/",
#     EnrollmentViewSet.as_view(
#         {
#             "post": "cancel",
#         }
#     ),
#     name="enrollment-cancel",
# ),
# ]

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

    # My enrollments
    path(
        "enrollments/my/",
        EnrollmentViewSet.as_view(
            {
                "get": "my_enrollments",
            }
        ),
        name="my-enrollments",
    ),


    # Enrollment detail
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


    # Cancel enrollment
    path(
        "gyms/<int:gym_id>/enrollments/<int:pk>/cancel/",
        EnrollmentViewSet.as_view(
            {
                "post": "cancel",
            }
        ),
        name="enrollment-cancel",
    ),

    # =========================================================
    # PAYMENTS
    # =========================================================

    # Payments list + create
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


    # My payments
    path(
        "payments/my/",
        PaymentViewSet.as_view(
            {
                "get": "my_payments",
            }
        ),
        name="my-payments",
    ),

    # Payment detail
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


    # Confirm payment
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
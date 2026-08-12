
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    GymViewSet,
    GymMembershipViewSet,
)


# =========================================================
# Router
# =========================================================

router = DefaultRouter()

router.register(
    "gym",
    GymViewSet,
)


urlpatterns = [

    # =====================================================
    # Gym APIs
    # =====================================================

    path(
        "",
        include(router.urls),
    ),

    # =====================================================
    # Gym Membership - List + Create
    #
    # GET  /api/gyms/{gym_id}/gymmembership/
    # POST /api/gyms/{gym_id}/gymmembership/
    # =====================================================

    path(
        "<int:gym_id>/gymmembership/",
        GymMembershipViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="gymmembership-list-create",
    ),

    # =====================================================
    # Gym Membership - Detail
    #
    # GET /api/gyms/{gym_id}/gymmembership/{pk}/
    # =====================================================

    path(
        "<int:gym_id>/gymmembership/<int:pk>/",
        GymMembershipViewSet.as_view(
            {
                "get": "retrieve",
            }
        ),
        name="gymmembership-detail",
    ),

    # =====================================================
    # Update Membership
    #
    # PATCH
    # /api/gyms/{gym_id}/gymmembership/{pk}/update_membership/
    #
    # تغییر:
    # - role
    # - salary
    # - share_percentage
    # =====================================================

    path(
        "<int:gym_id>/gymmembership/<int:pk>/update_membership/",
        GymMembershipViewSet.as_view(
            {
                "patch": "update_membership",
            }
        ),
        name="gymmembership-update-membership",
    ),

    # =====================================================
    # Deactivate
    #
    # POST
    # /api/gyms/{gym_id}/gymmembership/{pk}/deactivate/
    # =====================================================

    path(
        "<int:gym_id>/gymmembership/<int:pk>/deactivate/",
        GymMembershipViewSet.as_view(
            {
                "post": "deactivate",
            }
        ),
        name="gymmembership-deactivate",
    ),

    # =====================================================
    # Activate
    #
    # POST
    # /api/gyms/{gym_id}/gymmembership/{pk}/activate/
    # =====================================================

    path(
        "<int:gym_id>/gymmembership/<int:pk>/activate/",
        GymMembershipViewSet.as_view(
            {
                "post": "activate",
            }
        ),
        name="gymmembership-activate",
    ),
]

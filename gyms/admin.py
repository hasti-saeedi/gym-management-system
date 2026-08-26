# gyms/admin.py

from django.contrib import admin

from .models import Gym, GymMembership


@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    """
    Admin configuration for Gym.

    Provides:
        - Gym information management
        - Filtering by active status
        - Searching by name, phone, and email
        - Read-only timestamps
    """

    list_display = [
        "id",
        "name",
        "phone",
        "email",
        "is_active",
        "created_at",
    ]

    list_filter = [
        "is_active",
    ]

    search_fields = [
        "name",
        "phone",
        "email",
    ]

    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]

    list_display_links = [
        "name",
    ]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "address",
                    "phone",
                    "email",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_active",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )


@admin.register(GymMembership)
class GymMembershipAdmin(admin.ModelAdmin):
    """
    Admin configuration for GymMembership.

    Provides:
        - Membership and user management
        - Filtering by role, active status, and gym
        - Searching by username and gym name
        - Read-only membership ID and join date
        - Separate sections for membership,
          financial, status, and timestamp information
    """

    list_display = [
        "id",
        "user",
        "username",
        "gym",
        "role",
        "is_active",
        "joined_at",
    ]

    list_filter = [
        "role",
        "is_active",
        "gym",
    ]

    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "gym__name",
    ]

    readonly_fields = [
        "id",
        "joined_at",
    ]

    list_display_links = [
        "id",
        "user",
        "gym",
    ]

    fieldsets = (
        (
            "Membership Information",
            {
                "fields": (
                    "user",
                    "gym",
                    "role",
                )
            },
        ),
        (
            "Financial Information",
            {
                "fields": (
                    "share_percentage",
                    "salary",
                ),
                "description": (
                    "Share percentage is only for owners. "
                    "Salary is for managers, trainers, and staff."
                ),
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_active",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "joined_at",
                ),
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    @admin.display(
        description="Username",
        ordering="user__username",
    )
    def username(self, obj):
        """
        Return the username of the membership user.

        Used in list_display because Django Admin does not
        support relation lookups such as user__username
        directly inside list_display.
        """

        return obj.user.username
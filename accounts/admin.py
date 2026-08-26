from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Configure the Django admin interface for CustomUser.

    Extends Django's built-in UserAdmin to display, filter, search,
    and manage the custom phone and address fields.
    """

    list_display = (
        "id",
        "username",
        "email",
        "phone",
        "is_active",
        "is_staff",
        "date_joined",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "username",
        "email",
        "phone",
        "first_name",
        "last_name",
    )

    ordering = (
        "-date_joined",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "phone",
                    "address",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "phone",
                    "address",
                )
            },
        ),
    )
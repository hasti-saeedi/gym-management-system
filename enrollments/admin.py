from django.contrib import admin

from .models import Enrollment, Payment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """
    Configure the Django admin interface for enrollments.
    """

    list_display = [
        "id",
        "user",
        "gym_class",
        "status",
        "enrollment_type",
        "registered_at",
        "attended",
    ]

    list_filter = [
        "status",
        "enrollment_type",
        "attended",
        "gym_class",
    ]

    search_fields = [
        "user__username",
        "user__email",
        "gym_class__name",
    ]

    list_editable = [
        "status",
        "attended",
    ]

    readonly_fields = [
        "id",
        "registered_at",
    ]

    list_display_links = [
        "id",
        "user",
        "gym_class",
    ]

    fieldsets = (
        (
            "Enrollment Information",
            {
                "fields": (
                    "user",
                    "gym_class",
                    "enrollment_type",
                ),
            },
        ),
        (
            "Selected Sessions (for Single Enrollment)",
            {
                "fields": (
                    "selected_sessions",
                ),
                "classes": ("collapse",),
                "description": (
                    "Select specific sessions for single enrollment"
                ),
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "status",
                    "attended",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "registered_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Configure the Django admin interface for payments.
    """

    list_display = [
        "id",
        "enrollment",
        "amount",
        "status",
        "transaction_id",
        "created_at",
    ]

    list_filter = [
        "status",
    ]

    search_fields = [
        "enrollment__user__username",
        "transaction_id",
    ]

    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
    ]

    list_display_links = [
        "id",
        "enrollment",
    ]

    fieldsets = (
        (
            "Payment Information",
            {
                "fields": (
                    "enrollment",
                    "amount",
                    "status",
                    "transaction_id",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )
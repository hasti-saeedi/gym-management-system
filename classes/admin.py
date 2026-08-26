from django.contrib import admin
from django.utils.html import format_html

from accounts.models import CustomUser

from .models import ClassSession, GymClass


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    """
    Configure the Django admin interface for class sessions.

    Provides session filtering, searching, attendance information,
    cancellation management, and seat availability.
    """

    list_display = [
        "id",
        "gym_class",
        "start_time",
        "end_time",
        "trainer",
        "is_cancelled",
        "available_seats",
    ]

    list_filter = [
        "is_cancelled",
        "gym_class__category",
        "trainer",
    ]

    search_fields = [
        "gym_class__name",
        "trainer__username",
    ]

    list_editable = [
        "is_cancelled",
    ]

    readonly_fields = [
        "id",
        "created_at",
        "available_seats",
        "present_count",
        "absent_count",
        "display_attendance",
    ]

    list_display_links = [
        "id",
        "gym_class",
        "start_time",
    ]

    fieldsets = (
        (
            "Session Information",
            {
                "fields": (
                    "gym_class",
                    "trainer",
                    "start_time",
                    "end_time",
                )
            },
        ),
        (
            "Cancellation",
            {
                "fields": (
                    "is_cancelled",
                    "cancel_reason",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Attendance Data",
            {
                "fields": (
                    "attendance",
                    "display_attendance",
                    "present_count",
                    "absent_count",
                    "available_seats",
                ),
                "description": (
                    "Attendance is automatically updated when users enroll."
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )

    def display_attendance(self, obj):
        """
        Display attendance information using usernames instead of user IDs.

        Args:
            obj (ClassSession): The class session being displayed.

        Returns:
            str: Formatted attendance information for the session.
        """
        if not obj.attendance:
            return "No attendance data"

        result = []

        for user_id, data in obj.attendance.items():
            try:
                user = CustomUser.objects.get(id=int(user_id))
                status = (
                    "Present"
                    if data.get("present")
                    else "Absent"
                )

                single_session = (
                    " (Single Session)"
                    if data.get("single_session")
                    else ""
                )

                result.append(
                    f"{user.username}{single_session}: {status}"
                )

            except CustomUser.DoesNotExist:
                result.append(
                    f"User {user_id}: {data.get('present')}"
                )

        return format_html("<br>".join(result))

    display_attendance.short_description = "Attendance Details"

    def available_seats(self, obj):
        """
        Display the number of seats currently available.

        Args:
            obj (ClassSession): The class session being displayed.

        Returns:
            int: The number of available seats.
        """
        return obj.available_seats

    available_seats.short_description = "Available Seats"

    def present_count(self, obj):
        """
        Display the number of students marked as present.

        Args:
            obj (ClassSession): The class session being displayed.

        Returns:
            int: The number of present students.
        """
        return obj.present_count

    present_count.short_description = "Present Count"

    def absent_count(self, obj):
        """
        Display the number of students marked as absent.

        Args:
            obj (ClassSession): The class session being displayed.

        Returns:
            int: The number of absent students.
        """
        return obj.absent_count

    absent_count.short_description = "Absent Count"


@admin.register(GymClass)
class GymClassAdmin(admin.ModelAdmin):
    """
    Configure the Django admin interface for gym classes.

    Provides class filtering, searching, session generation,
    and management of class information.
    """

    list_display = [
        "id",
        "name",
        "gym",
        "trainer",
        "category",
        "capacity",
        "price",
        "is_active",
        "start_date",
        "end_date",
        "total_sessions",
    ]

    search_fields = [
        "name",
        "gym__name",
        "trainer__username",
    ]

    list_filter = [
        "category",
        "gym",
        "is_active",
    ]

    readonly_fields = [
        "id",
        "created_at",
    ]

    actions = [
        "generate_sessions_action",
    ]

    @admin.action(description="Generate sessions")
    def generate_sessions_action(self, request, queryset):
        """
        Generate class sessions for the selected gym classes.

        Args:
            request: The current admin request.
            queryset: The selected GymClass objects.
        """
        from .services.gym_class_services import generate_sessions

        for gym_class in queryset:
            generate_sessions(gym_class)

        self.message_user(
            request,
            "Sessions generated successfully.",
        )
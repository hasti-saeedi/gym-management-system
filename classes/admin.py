from django.contrib import admin
from django.utils.html import format_html  # ← اضافه کن
from .models import GymClass, ClassSession

@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):

    list_display = ['id', 'gym_class', 'start_time', 'end_time', 'trainer', 'is_cancelled', 'available_seats']
    list_filter = ['is_cancelled', 'gym_class__category', 'trainer']
    search_fields = ['gym_class__name', 'trainer__username']
    list_editable = ['is_cancelled']
    readonly_fields = ['id', 'created_at', 'available_seats', 'present_count', 'absent_count', 'display_attendance']
    list_display_links = ['id', 'gym_class', 'start_time']
    
    def display_attendance(self, obj):
        """نمایش attendance با نام کاربر به جای id"""
        if not obj.attendance:
            return "No attendance data"
        
        result = []
        for user_id, data in obj.attendance.items():
            try:
                from accounts.models import CustomUser
                user = CustomUser.objects.get(id=int(user_id))
                status = "✓ حاضر" if data.get('present') else "✗ غایب"
                single = " (تک جلسه)" if data.get('single_session') else ""
                result.append(f"{user.username}{single}: {status}")
            except:
                result.append(f"User {user_id}: {data.get('present')}")
        
        return format_html("<br>".join(result))  # ← استفاده از format_html
    display_attendance.short_description = 'Attendance Details'
    
    fieldsets = (
        ('Session Information', {
            'fields': ('gym_class', 'trainer', 'start_time', 'end_time')
        }),
        ('Cancellation', {
            'fields': ('is_cancelled', 'cancel_reason'),
            'classes': ('collapse',)
        }),
        ('Attendance Data', {
            'fields': ('attendance', 'display_attendance', 'present_count', 'absent_count', 'available_seats'),
            'description': 'Attendance is automatically updated when users enroll.'
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def available_seats(self, obj):
        return obj.available_seats
    available_seats.short_description = 'Available Seats'
    
    def present_count(self, obj):
        return obj.present_count
    present_count.short_description = 'Present Count'
    
    def absent_count(self, obj):
        return obj.absent_count
    absent_count.short_description = 'Absent Count'


@admin.register(GymClass)
class GymClassAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'name',
        'gym',
        'trainer',
        'category',
        'capacity',
        'price',
        'is_active',
        'start_date',
        'end_date',
        'total_sessions',
    ]

    search_fields = ['name', 'gym__name', 'trainer__username']
    list_filter = ['category', 'gym', 'is_active']
    readonly_fields = ['id', 'created_at']

    actions = ['generate_sessions_action']

    @admin.action(description="Generate sessions")
    def generate_sessions_action(self, request, queryset):
        from .services.gym_class_services import generate_sessions

        for gym_class in queryset:
            generate_sessions(gym_class)

        self.message_user(
            request,
            "Sessions generated successfully."
        )
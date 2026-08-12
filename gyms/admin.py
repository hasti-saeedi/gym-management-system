# gyms/admin.py
from django.contrib import admin
from .models import Gym, GymMembership


@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'phone', 'email', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'phone', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_display_links = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'address', 'phone', 'email')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GymMembership)
class GymMembershipAdmin(admin.ModelAdmin):
    list_display = ['id','user', 'user__username', 'gym', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'gym']
    search_fields = ['user__username', 'gym__name']
    readonly_fields = ['id', 'joined_at']
    list_display_links = ['id','user', 'gym']

    fieldsets = (
        ('Membership Information', {
            'fields': ('user', 'gym', 'role')
        }),
        ('Financial Information', {
            'fields': ('share_percentage', 'salary'),
            'description': 'Share percentage is only for owners. Salary is for managers, trainers, and staff.'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('joined_at',),
            'classes': ('collapse',)
        }),
    )
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    list_display = ('id','username', 'email', 'phone', 'is_active', 'is_staff', 'date_joined')
    
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    
    ordering = ('-date_joined',) # با - چون میخواهیم جدید ترین را نشان دهد

 
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone', 'address')}),
    )# چون این سه فیلد در ابسترک یوزر نیست ممکن بود این رو در دسته بندی نمایش نده  الان گفتی اینها رو در دسته بندی ادیشنال اینفو بنویس
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('phone', 'address')}),
    )


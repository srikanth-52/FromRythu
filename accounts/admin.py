from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmailOTP

@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'otp', 'created_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('email', 'otp', 'user__username')

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'role', 'phone_number', 'city', 'state', 'is_verified', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_active', 'state')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'city')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('FromRythu Marketplace Role & Details', {
            'fields': ('role', 'phone_number', 'address', 'city', 'state', 'pincode', 'profile_picture', 'is_verified'),
        }),
    )

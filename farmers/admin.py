from django.contrib import admin
from .models import FarmerProfile

@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ('farm_name', 'user', 'district', 'state', 'farming_type', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'farming_type', 'state', 'district')
    search_fields = ('farm_name', 'user__username', 'user__first_name', 'primary_crops', 'district')
    actions = ['approve_farmers', 'revoke_approval']

    def approve_farmers(self, request, queryset):
        queryset.update(is_approved=True)
        for profile in queryset:
            profile.user.is_verified = True
            profile.user.save()
        self.message_user(request, f"{queryset.count()} farmer profiles have been approved.")
    approve_farmers.short_description = "Approve and verify selected Farmers"

    def revoke_approval(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"Approval revoked for {queryset.count()} farmers.")
    revoke_approval.short_description = "Revoke approval"

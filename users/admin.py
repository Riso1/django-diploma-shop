from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from .models import Profile

User = get_user_model()


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "phone", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "full_name", "phone")
    readonly_fields = ("created_at", "updated_at")


class SoftDeleteUserAdmin(DefaultUserAdmin):
    actions = ["restore_users"]

    def delete_model(self, request, obj):
        obj.is_active = False
        obj.save(update_fields=["is_active"])

    def delete_queryset(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Восстановить выбранных пользователей")
    def restore_users(self, request, queryset):
        queryset.update(is_active=True)


try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(User, SoftDeleteUserAdmin)

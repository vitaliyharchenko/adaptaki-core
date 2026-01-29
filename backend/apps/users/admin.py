from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser")
    search_fields = ("username",)
    ordering = ("id",)


admin.site.unregister(Group)

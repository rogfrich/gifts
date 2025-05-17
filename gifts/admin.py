from django.contrib import admin

from .models import Wish


@admin.register(Wish)
class WishAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "claimed", "claimed_by", "created_at", "updated_at")

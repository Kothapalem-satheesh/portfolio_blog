from django.contrib import admin

from .models import PostNotificationLog, Subscriber


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "created_at", "verified_at")
    search_fields = ("email",)
    list_filter = ("is_active",)


@admin.register(PostNotificationLog)
class PostNotificationLogAdmin(admin.ModelAdmin):
    list_display = ("post", "subscriber", "status", "sent_at")
    list_filter = ("status",)

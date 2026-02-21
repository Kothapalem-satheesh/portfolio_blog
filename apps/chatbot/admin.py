from django.contrib import admin

from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("user", "session_key", "created_at")
    search_fields = ("user_message", "assistant_message", "session_key")

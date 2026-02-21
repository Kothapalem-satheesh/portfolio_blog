from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "is_approved", "created_at")
    list_filter = ("is_approved",)
    search_fields = ("body", "author__username", "post__title")

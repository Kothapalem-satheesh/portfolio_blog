from django.contrib import admin

from .models import BlogPost, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "published_at", "created_at")
    list_filter = ("status", "category")
    search_fields = ("title", "content", "excerpt", "tags")
    prepopulated_fields = {"slug": ("title",)}

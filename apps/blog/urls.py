from django.urls import path

from .views import blog_create_view, blog_delete_view, blog_detail_view, blog_edit_view, blog_list_view

urlpatterns = [
    path("", blog_list_view, name="blog_list"),
    path("new/", blog_create_view, name="blog_create"),
    path("<slug:slug>/", blog_detail_view, name="blog_detail"),
    path("<slug:slug>/edit/", blog_edit_view, name="blog_edit"),
    path("<slug:slug>/delete/", blog_delete_view, name="blog_delete"),
]

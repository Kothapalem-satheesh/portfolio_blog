from django.urls import path

from .views import approve_comment_view, create_comment_view, delete_comment_view

urlpatterns = [
    path("add/<slug:slug>/", create_comment_view, name="comment_create"),
    path("<int:pk>/approve/", approve_comment_view, name="comment_approve"),
    path("<int:pk>/delete/", delete_comment_view, name="comment_delete"),
]

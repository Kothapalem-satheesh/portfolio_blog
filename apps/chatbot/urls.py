from django.urls import path

from .views import chat_api_view

urlpatterns = [
    path("", chat_api_view, name="chat_api"),
]

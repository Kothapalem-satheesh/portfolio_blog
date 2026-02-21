from django.urls import path

from .views import (
    notify_subscribers_view,
    subscribe_view,
    subscriber_delete_view,
    subscriber_toggle_view,
    subscribers_list_view,
    unsubscribe_view,
    verify_subscription_view,
)

urlpatterns = [
    path("", subscribe_view, name="subscribe"),
    path("verify/<str:token>/", verify_subscription_view, name="verify_subscription"),
    path("unsubscribe/<str:token>/", unsubscribe_view, name="unsubscribe"),

    # Dashboard subscriber management
    path("dashboard/", subscribers_list_view, name="subscribers_list"),
    path("dashboard/<int:pk>/toggle/", subscriber_toggle_view, name="subscriber_toggle"),
    path("dashboard/<int:pk>/delete/", subscriber_delete_view, name="subscriber_delete"),
    path("notify/<int:post_id>/", notify_subscribers_view, name="notify_subscribers"),
]

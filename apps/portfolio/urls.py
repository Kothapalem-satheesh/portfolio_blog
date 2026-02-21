from django.urls import path

from .views import (
    about_view,
    contact_view,
    dashboard_view,
    home_view,
    message_delete_view,
    message_reply_view,
    messages_inbox_view,
    profile_edit_view,
    project_create_view,
    project_delete_view,
    project_edit_view,
    projects_view,
    skill_create_view,
    skill_delete_view,
    skill_edit_view,
)

urlpatterns = [
    path("", home_view, name="home"),
    path("about/", about_view, name="about"),
    path("projects/", projects_view, name="projects"),
    path("contact/", contact_view, name="contact"),

    # Dashboard
    path("dashboard/", dashboard_view, name="dashboard"),
    path("dashboard/profile/", profile_edit_view, name="profile_edit"),
    path("dashboard/messages/", messages_inbox_view, name="messages_inbox"),
    path("dashboard/messages/<int:pk>/reply/", message_reply_view, name="message_reply"),
    path("dashboard/messages/<int:pk>/delete/", message_delete_view, name="message_delete"),

    # Projects
    path("dashboard/projects/add/", project_create_view, name="project_create"),
    path("dashboard/projects/<int:pk>/edit/", project_edit_view, name="project_edit"),
    path("dashboard/projects/<int:pk>/delete/", project_delete_view, name="project_delete"),

    # Skills
    path("dashboard/skills/add/", skill_create_view, name="skill_create"),
    path("dashboard/skills/<int:pk>/edit/", skill_edit_view, name="skill_edit"),
    path("dashboard/skills/<int:pk>/delete/", skill_delete_view, name="skill_delete"),
]

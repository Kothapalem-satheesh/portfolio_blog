import logging
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone

from apps.blog.models import BlogPost
from apps.comments.models import Comment
from apps.subscriptions.models import Subscriber

from .forms import ContactForm, EducationForm, ProfileForm, ProjectForm, SkillForm
from .models import ContactMessage, Education, Profile, Project, Skill
from .resume_defaults import (
    DEFAULT_ACHIEVEMENTS,
    DEFAULT_EDUCATION,
    DEFAULT_INTERNSHIPS,
    DEFAULT_PROJECTS,
    DEFAULT_SKILLS,
)

logger = logging.getLogger(__name__)

_staff = lambda u: u.is_staff  # noqa: E731


# ─── Public pages ────────────────────────────────────────────────────────────

def home_view(request):
    featured_projects = list(Project.objects.filter(featured=True)[:1])
    if not featured_projects:
        featured_projects = DEFAULT_PROJECTS[:1]
    context = {
        "featured_projects": featured_projects,
        "latest_posts": BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED)[:1],
    }
    return render(request, "portfolio/home.html", context)


def about_view(request):
    education_items = list(Education.objects.all())
    if not education_items:
        education_items = DEFAULT_EDUCATION

    skills = list(Skill.objects.all().order_by("category", "order", "name"))
    if not skills:
        skills = DEFAULT_SKILLS

    projects = list(Project.objects.all())
    if not projects:
        projects = DEFAULT_PROJECTS

    return render(request, "portfolio/about.html", {
        "education_items": education_items,
        "skills": skills,
        "projects": projects,
        "internships": DEFAULT_INTERNSHIPS,
        "achievements": DEFAULT_ACHIEVEMENTS,
    })


def projects_view(request):
    projects = list(Project.objects.all())
    if not projects:
        projects = DEFAULT_PROJECTS
    return render(request, "portfolio/projects.html", {"projects": projects})


def _send_html_email(subject, template_html, template_txt, context, recipient):
    """Helper: send a dual-format (HTML + plain text) email."""
    html_body = render_to_string(template_html, context)
    text_body = render_to_string(template_txt, context)
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # ── Save to database ──────────────────────────────
            ContactMessage.objects.create(
                name=data["name"],
                email=data["email"],
                subject=data["subject"],
                message=data["message"],
            )
            # ── Send emails ───────────────────────────────────
            ctx = {
                "name":        data["name"],
                "email":       data["email"],
                "subject":     data["subject"],
                "message":     data["message"],
                "received_at": timezone.now().strftime("%B %d, %Y at %H:%M UTC"),
                "site_url":    settings.SITE_BASE_URL,
            }
            try:
                _send_html_email(
                    subject=f"📬 New Contact: {data['subject']}",
                    template_html="emails/contact_admin.html",
                    template_txt="emails/contact_admin.txt",
                    context=ctx,
                    recipient=settings.ADMIN_EMAIL,
                )
                _send_html_email(
                    subject="✅ We received your message",
                    template_html="emails/contact_user.html",
                    template_txt="emails/contact_user.txt",
                    context=ctx,
                    recipient=data["email"],
                )
                messages.success(
                    request,
                    "Your message was sent! Check your inbox for a confirmation copy.",
                )
            except Exception:
                logger.exception("Contact email failed")
                messages.warning(
                    request,
                    "Message saved, but email delivery failed. I'll still see it in the dashboard.",
                )
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "portfolio/contact.html", {"form": form})


# ─── Dashboard ───────────────────────────────────────────────────────────────

@login_required
@user_passes_test(_staff)
def dashboard_view(request):
    context = {
        "post_count":        BlogPost.objects.count(),
        "published_count":   BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).count(),
        "draft_count":       BlogPost.objects.filter(status=BlogPost.Status.DRAFT).count(),
        "subscriber_count":  Subscriber.objects.filter(is_active=True).count(),
        "pending_comments":  Comment.objects.filter(is_approved=False).count(),
        "project_count":     Project.objects.count(),
        "unread_messages":   ContactMessage.objects.filter(is_read=False).count(),
        "recent_posts":      BlogPost.objects.order_by("-created_at")[:8],
        "pending_comment_list": Comment.objects.filter(is_approved=False).select_related("author", "post")[:10],
        "projects":          Project.objects.order_by("order", "-id")[:20],
        "skills":            Skill.objects.order_by("order")[:20],
        "recent_messages":   ContactMessage.objects.all()[:5],
    }
    return render(request, "dashboard/index.html", context)


@login_required
@user_passes_test(_staff)
def messages_inbox_view(request):
    msgs = ContactMessage.objects.all()
    # mark all as read when inbox is opened
    ContactMessage.objects.filter(is_read=False).update(is_read=True)
    return render(request, "dashboard/messages.html", {"contact_messages": msgs})


@login_required
@user_passes_test(_staff)
def message_reply_view(request, pk):
    contact_msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        reply_body = request.POST.get("reply_body", "").strip()
        if not reply_body:
            messages.error(request, "Reply cannot be empty.")
            return redirect("message_reply", pk=pk)
        ctx = {
            "name":       contact_msg.name,
            "subject":    contact_msg.subject,
            "original":   contact_msg.message,
            "reply_body": reply_body,
            "site_url":   settings.SITE_BASE_URL,
        }
        try:
            _send_html_email(
                subject=f"Re: {contact_msg.subject}",
                template_html="emails/reply_user.html",
                template_txt="emails/reply_user.txt",
                context=ctx,
                recipient=contact_msg.email,
            )
            contact_msg.is_read = True
            contact_msg.save(update_fields=["is_read"])
            messages.success(request, f"Reply sent to {contact_msg.name} ({contact_msg.email}).")
            return redirect("messages_inbox")
        except Exception:
            logger.exception("Reply email failed")
            messages.error(request, "Failed to send reply. Check your email settings.")
    return render(request, "dashboard/message_reply.html", {"contact_msg": contact_msg})


@login_required
@user_passes_test(_staff)
def message_delete_view(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        msg.delete()
        messages.success(request, "Message deleted.")
    return redirect("messages_inbox")


# ─── Profile ─────────────────────────────────────────────────────────────────

@login_required
@user_passes_test(_staff)
def profile_edit_view(request):
    profile = Profile.objects.order_by("-updated_at").first()
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("dashboard")
    return render(request, "dashboard/profile_edit.html", {"form": form, "profile": profile})


# ─── Projects ────────────────────────────────────────────────────────────────

@login_required
@user_passes_test(_staff)
def project_create_view(request):
    form = ProjectForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project added.")
        return redirect("dashboard")
    return render(request, "dashboard/project_form.html", {"form": form, "is_create": True})


@login_required
@user_passes_test(_staff)
def project_edit_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST or None, request.FILES or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project updated.")
        return redirect("dashboard")
    return render(request, "dashboard/project_form.html", {"form": form, "project": project})


@login_required
@user_passes_test(_staff)
def project_delete_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        project.delete()
        messages.success(request, f'Project "{project.title}" deleted.')
        return redirect("dashboard")
    return render(request, "dashboard/confirm_delete.html", {"object": project, "type": "Project"})


# ─── Skills ──────────────────────────────────────────────────────────────────

@login_required
@user_passes_test(_staff)
def skill_create_view(request):
    form = SkillForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill added.")
        return redirect("dashboard")
    return render(request, "dashboard/skill_form.html", {"form": form, "is_create": True})


@login_required
@user_passes_test(_staff)
def skill_edit_view(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    form = SkillForm(request.POST or None, instance=skill)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill updated.")
        return redirect("dashboard")
    return render(request, "dashboard/skill_form.html", {"form": form, "skill": skill})


@login_required
@user_passes_test(_staff)
def skill_delete_view(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if request.method == "POST":
        skill.delete()
        messages.success(request, f'Skill "{skill.name}" deleted.')
        return redirect("dashboard")
    return render(request, "dashboard/confirm_delete.html", {"object": skill, "type": "Skill"})

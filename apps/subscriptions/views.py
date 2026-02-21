import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from .forms import SubscribeForm
from .models import PostNotificationLog, Subscriber

logger = logging.getLogger(__name__)
_staff = lambda u: u.is_staff  # noqa: E731


# ─── Public ──────────────────────────────────────────────────────────────────

def subscribe_view(request):
    if request.method == "POST":
        form = SubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            subscriber, created = Subscriber.objects.get_or_create(email=email)

            if not created:
                # Email already in database — tell them and do nothing else
                messages.warning(
                    request,
                    "You're already subscribed with that email address! "
                    "You'll receive an email whenever a new post is published.",
                )
                return redirect("subscribe")

            # Brand-new subscriber — activate immediately, send welcome email
            subscriber.is_active = True
            subscriber.verified_at = timezone.now()
            subscriber.save(update_fields=["is_active", "verified_at"])

            unsubscribe_path = reverse("unsubscribe", kwargs={"token": subscriber.verify_token})
            unsubscribe_url = f"{settings.SITE_BASE_URL}{unsubscribe_path}"

            ctx = {
                "site_url": settings.SITE_BASE_URL,
                "unsubscribe_url": unsubscribe_url,
            }
            html = render_to_string("emails/welcome_subscriber.html", ctx)
            text = render_to_string("emails/welcome_subscriber.txt", ctx)

            msg = EmailMultiAlternatives(
                subject="You're subscribed! — Kothapalem Satheesh Blog",
                body=text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[subscriber.email],
            )
            msg.attach_alternative(html, "text/html")
            try:
                msg.send(fail_silently=False)
            except Exception:
                logger.exception("Welcome email failed for %s", email)

            messages.success(request, "You're subscribed! 🎉 Check your inbox for a welcome email.")
            return redirect("home")
    else:
        form = SubscribeForm()
    return render(request, "portfolio/subscribe.html", {"form": form})


def verify_subscription_view(request, token):
    subscriber = get_object_or_404(Subscriber, verify_token=token)
    subscriber.is_active = True
    subscriber.verified_at = timezone.now()
    subscriber.save(update_fields=["is_active", "verified_at"])
    messages.success(request, "You're subscribed! You'll get an email whenever a new post is published.")
    return redirect("home")


def unsubscribe_view(request, token):
    subscriber = get_object_or_404(Subscriber, verify_token=token)
    subscriber.is_active = False
    subscriber.save(update_fields=["is_active"])
    messages.success(request, "You've been unsubscribed successfully.")
    return redirect("home")


# ─── Dashboard subscriber management ─────────────────────────────────────────

@login_required
@user_passes_test(_staff)
def subscribers_list_view(request):
    """Dashboard: list all subscribers, add new ones directly as active."""
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        if email:
            sub, created = Subscriber.objects.get_or_create(email=email)
            if not sub.is_active:
                sub.is_active = True
                sub.verified_at = timezone.now()
                sub.save(update_fields=["is_active", "verified_at"])
            if created:
                messages.success(request, f"{email} added as an active subscriber.")
            else:
                messages.success(request, f"{email} already exists — marked as active.")
        return redirect("subscribers_list")

    subs = Subscriber.objects.order_by("-created_at")
    return render(request, "dashboard/subscribers.html", {
        "subscribers": subs,
        "active_count":   subs.filter(is_active=True).count(),
        "inactive_count": subs.filter(is_active=False).count(),
    })


@login_required
@user_passes_test(_staff)
def subscriber_toggle_view(request, pk):
    """Activate or deactivate a subscriber."""
    sub = get_object_or_404(Subscriber, pk=pk)
    if request.method == "POST":
        sub.is_active = not sub.is_active
        if sub.is_active:
            sub.verified_at = timezone.now()
        sub.save(update_fields=["is_active", "verified_at"])
        status = "activated" if sub.is_active else "deactivated"
        messages.success(request, f"{sub.email} {status}.")
    return redirect("subscribers_list")


@login_required
@user_passes_test(_staff)
def subscriber_delete_view(request, pk):
    """Delete a subscriber entirely."""
    sub = get_object_or_404(Subscriber, pk=pk)
    if request.method == "POST":
        email = sub.email
        sub.delete()
        messages.success(request, f"{email} removed.")
    return redirect("subscribers_list")


@login_required
@user_passes_test(_staff)
def notify_subscribers_view(request, post_id):
    """Manually trigger notification emails for a specific post."""
    from apps.blog.models import BlogPost
    from .services import send_post_email

    post = get_object_or_404(BlogPost, pk=post_id)

    if post.status != BlogPost.Status.PUBLISHED:
        messages.error(request, "Only published posts can be sent to subscribers. Publish it first.")
        return redirect("dashboard")

    subscribers = Subscriber.objects.filter(is_active=True)
    if not subscribers.exists():
        messages.warning(request, "No active subscribers yet.")
        return redirect("dashboard")

    sent = 0
    skipped = 0
    failed = 0

    for sub in subscribers:
        already_sent = PostNotificationLog.objects.filter(post=post, subscriber=sub).exists()
        if already_sent:
            skipped += 1
            continue
        try:
            send_post_email(subscriber_email=sub.email, post=post, subscriber=sub)
            PostNotificationLog.objects.create(post=post, subscriber=sub, status="sent")
            sent += 1
        except Exception as exc:
            logger.exception("Manual notify failed for %s", sub.email)
            PostNotificationLog.objects.create(post=post, subscriber=sub, status="failed", error=str(exc))
            failed += 1

    parts = []
    if sent:    parts.append(f"{sent} email{'s' if sent != 1 else ''} sent")
    if skipped: parts.append(f"{skipped} already notified")
    if failed:  parts.append(f"{failed} failed")

    msg_text = " · ".join(parts) if parts else "Nothing to send"
    if failed:
        messages.warning(request, f"Notification done — {msg_text}. Check email settings for failures.")
    else:
        messages.success(request, f"Notification done — {msg_text}.")

    return redirect("dashboard")

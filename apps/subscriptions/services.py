import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

logger = logging.getLogger(__name__)


def send_post_email(*, subscriber_email: str, post, subscriber=None):
    post_url = f"{settings.SITE_BASE_URL}{post.get_absolute_url()}"

    unsubscribe_url = ""
    if subscriber and subscriber.verify_token:
        path = reverse("unsubscribe", kwargs={"token": subscriber.verify_token})
        unsubscribe_url = f"{settings.SITE_BASE_URL}{path}"

    ctx = {
        "post":            post,
        "post_url":        post_url,
        "unsubscribe_url": unsubscribe_url,
        "site_url":        settings.SITE_BASE_URL,
    }

    subject   = f"📝 New Post: {post.title}"
    html_body = render_to_string("emails/new_post.html", ctx)
    text_body = render_to_string("emails/new_post.txt",  ctx)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[subscriber_email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)

    logger.info("New post email sent to %s for post=%s", subscriber_email, post.id)

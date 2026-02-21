from celery import shared_task

from apps.blog.models import BlogPost

from .models import PostNotificationLog, Subscriber
from .services import send_post_email


@shared_task
def send_new_post_notifications(post_id: int):
    post = BlogPost.objects.get(pk=post_id)
    subscribers = Subscriber.objects.filter(is_active=True)
    for subscriber in subscribers:
        if PostNotificationLog.objects.filter(post=post, subscriber=subscriber).exists():
            continue
        try:
            send_post_email(
                subscriber_email=subscriber.email,
                post=post,
                subscriber=subscriber,
            )
            PostNotificationLog.objects.create(post=post, subscriber=subscriber, status="sent")
        except Exception as exc:  # pragma: no cover
            PostNotificationLog.objects.create(
                post=post, subscriber=subscriber, status="failed", error=str(exc)
            )

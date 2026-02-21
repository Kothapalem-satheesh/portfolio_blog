import secrets

from django.db import models


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    verify_token = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.verify_token:
            self.verify_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class PostNotificationLog(models.Model):
    post = models.ForeignKey("blog.BlogPost", on_delete=models.CASCADE, related_name="notification_logs")
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name="notification_logs")
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="sent")
    error = models.TextField(blank=True)

    class Meta:
        unique_together = ("post", "subscriber")

    def __str__(self):
        return f"{self.post_id} -> {self.subscriber.email}"

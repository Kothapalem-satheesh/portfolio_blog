from django.conf import settings
from django.db import models, transaction
from django.template.defaultfilters import slugify
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    cover_image = models.ImageField(upload_to="blog/", blank=True, null=True)
    tags = models.CharField(max_length=220, blank=True, help_text="Comma-separated tags")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def save(self, *args, **kwargs):
        from django.utils import timezone

        was_published = None
        if self.pk:
            was_published = BlogPost.objects.filter(pk=self.pk, status=BlogPost.Status.PUBLISHED).exists()

        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == BlogPost.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

        newly_published = self.status == BlogPost.Status.PUBLISHED and not was_published
        if newly_published:
            post_id = self.id

            def _notify():
                from apps.subscriptions.tasks import send_new_post_notifications
                send_new_post_notifications.delay(post_id)

            # Run AFTER the transaction commits so the post is readable by the task
            transaction.on_commit(_notify)

    def get_absolute_url(self):
        return reverse("blog_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title

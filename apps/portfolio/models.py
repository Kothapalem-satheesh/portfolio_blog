from django.db import models


class Profile(models.Model):
    full_name = models.CharField(max_length=120)
    title = models.CharField(max_length=140)
    intro = models.TextField()
    about = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=120, blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    resume_url = models.URLField(blank=True)
    photo      = models.ImageField(upload_to="profile/", blank=True, null=True)
    hero_video = models.FileField(upload_to="videos/", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class Education(models.Model):
    degree = models.CharField(max_length=120)
    institution = models.CharField(max_length=140)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-start_year"]

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Skill(models.Model):
    name = models.CharField(max_length=80, unique=True)
    category = models.CharField(max_length=80, blank=True)
    level = models.PositiveIntegerField(default=70)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class ContactMessage(models.Model):
    name       = models.CharField(max_length=120)
    email      = models.EmailField()
    subject    = models.CharField(max_length=160)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.subject}"


class Project(models.Model):
    title = models.CharField(max_length=140)
    summary = models.TextField()
    tech_stack = models.CharField(max_length=200, blank=True)
    demo_url = models.URLField(blank=True)
    source_url = models.URLField(blank=True)
    image = models.ImageField(upload_to="projects/", blank=True, null=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-id"]

    def __str__(self):
        return self.title

from django.contrib.auth.models import User
from django.test import TestCase

from .models import BlogPost


class BlogPostModelTest(TestCase):
    def test_slug_and_publish_date_set_for_published_post(self):
        author = User.objects.create_user(username="writer", password="pass1234")
        post = BlogPost.objects.create(
            title="My First Article",
            author=author,
            content="Hello world",
            status=BlogPost.Status.PUBLISHED,
        )
        self.assertEqual(post.slug, "my-first-article")
        self.assertIsNotNone(post.published_at)

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import BlogPost


class CommentPermissionTest(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pass1234")
        self.reader = User.objects.create_user(username="reader", password="pass1234")
        self.post = BlogPost.objects.create(
            title="Post",
            author=self.author,
            content="Text",
            status=BlogPost.Status.PUBLISHED,
        )

    def test_guest_cannot_comment(self):
        response = self.client.post(reverse("comment_create", kwargs={"slug": self.post.slug}), {"body": "Hi"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_signed_in_user_can_submit_comment(self):
        self.client.login(username="reader", password="pass1234")
        response = self.client.post(reverse("comment_create", kwargs={"slug": self.post.slug}), {"body": "Hi"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.post.comments.count(), 1)

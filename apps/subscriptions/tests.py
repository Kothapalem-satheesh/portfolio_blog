from django.test import TestCase
from django.urls import reverse

from .models import Subscriber


class SubscriptionFlowTest(TestCase):
    def test_verify_endpoint_activates_subscriber(self):
        subscriber = Subscriber.objects.create(email="test@example.com")
        response = self.client.get(reverse("verify_subscription", kwargs={"token": subscriber.verify_token}))
        subscriber.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(subscriber.is_active)

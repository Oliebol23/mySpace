import time

from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContactMessage


class PageTests(TestCase):
    def test_public_pages_load(self):
        for name in ("home", "about", "contact"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    EMAIL_HOST_USER="website@example.com",
    DEFAULT_FROM_EMAIL="website@example.com",
    CONTACT_EMAIL="owner@example.com",
    CONTACT_MIN_FILL_SECONDS=0,
    CONTACT_RATE_LIMIT=5,
    CONTACT_RATE_WINDOW_SECONDS=3600,
)
class ContactFormTests(TestCase):
    def setUp(self):
        cache.clear()

    def _valid_data(self, **overrides):
        data = {
            "name": "Test Visitor",
            "email": "visitor@example.com",
            "message": "Hello from the website.",
            "website": "",
        }
        data.update(overrides)
        return data

    def test_valid_contact_message_is_saved_and_emailed(self):
        self.client.get(reverse("contact"))
        response = self.client.post(reverse("contact"), self._valid_data())

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_success.html")
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "New message from your website")
        self.assertEqual(mail.outbox[0].to, ["owner@example.com"])
        self.assertEqual(mail.outbox[0].reply_to, ["visitor@example.com"])

    def test_honeypot_blocks_bot_submission(self):
        self.client.get(reverse("contact"))
        response = self.client.post(
            reverse("contact"),
            self._valid_data(website="https://spam.example"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact.html")
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(CONTACT_RATE_LIMIT=1)
    def test_rate_limit_blocks_repeated_submission(self):
        self.client.get(reverse("contact"))
        first = self.client.post(
            reverse("contact"),
            self._valid_data(),
            REMOTE_ADDR="203.0.113.10",
        )
        self.assertTemplateUsed(first, "contact_success.html")

        self.client.get(reverse("contact"))
        second = self.client.post(
            reverse("contact"),
            self._valid_data(message="Second message"),
            REMOTE_ADDR="203.0.113.10",
        )

        self.assertTemplateUsed(second, "contact.html")
        self.assertContains(second, "Too many messages")
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(CONTACT_MIN_FILL_SECONDS=5)
    def test_too_fast_submission_is_rejected(self):
        self.client.get(reverse("contact"))
        session = self.client.session
        session["contact_form_started_at"] = time.time()
        session.save()

        response = self.client.post(reverse("contact"), self._valid_data())

        self.assertTemplateUsed(response, "contact.html")
        self.assertContains(response, "submitted a little too quickly")
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

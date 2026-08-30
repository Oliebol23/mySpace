from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContactMessage


class PageTests(TestCase):
    def test_public_pages_load(self):
        for name in ("home", "about", "contact"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200)


class ContactFormTests(TestCase):
    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        EMAIL_HOST_USER="website@example.com",
        DEFAULT_FROM_EMAIL="website@example.com",
        CONTACT_EMAIL="owner@example.com",
    )
    def test_valid_contact_message_is_saved_and_emailed(self):
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Test Visitor",
                "email": "visitor@example.com",
                "message": "Hello from the website.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_success.html")
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Test Visitor", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ["owner@example.com"])
        self.assertEqual(mail.outbox[0].reply_to, ["visitor@example.com"])

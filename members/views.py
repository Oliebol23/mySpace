import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import render

from .forms import ContactForm

logger = logging.getLogger(__name__)


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            _send_contact_notification(contact_message)
            return render(
                request,
                "contact_success.html",
                {"name": contact_message.name},
            )
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})


def _send_contact_notification(contact_message):
    """Email the site owner when mail settings are configured.

    The message is already stored in the database before this function runs,
    so an SMTP problem never loses a contact submission.
    """
    if not settings.CONTACT_EMAIL or not settings.EMAIL_HOST_USER:
        return

    try:
        email = EmailMessage(
            subject=f"New website message from {contact_message.name}",
            body=(
                f"Name: {contact_message.name}\n"
                f"Email: {contact_message.email}\n\n"
                f"Message:\n{contact_message.message}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_EMAIL],
            reply_to=[contact_message.email],
        )
        email.send(fail_silently=False)
    except Exception:
        logger.exception("Could not send contact-form notification email")

import hashlib
import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.shortcuts import render

from .forms import ContactForm

logger = logging.getLogger(__name__)
CONTACT_STARTED_SESSION_KEY = "contact_form_started_at"


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            if _submitted_too_quickly(request):
                form.add_error(
                    None,
                    "That was submitted a little too quickly. Please try once more.",
                )
            elif _contact_rate_limit_reached(request):
                form.add_error(
                    None,
                    "Too many messages were sent recently. Please try again later.",
                )
            else:
                contact_message = form.save()
                _record_contact_submission(request)
                _send_contact_notification(contact_message)
                request.session.pop(CONTACT_STARTED_SESSION_KEY, None)
                return render(
                    request,
                    "contact_success.html",
                    {"name": contact_message.name},
                )

        # If someone POSTed directly without first loading the form, or if a
        # too-fast submission was rejected, start a fresh timing window so a
        # normal retry can succeed.
        if CONTACT_STARTED_SESSION_KEY not in request.session or form.non_field_errors():
            request.session[CONTACT_STARTED_SESSION_KEY] = time.time()
    else:
        form = ContactForm()
        request.session[CONTACT_STARTED_SESSION_KEY] = time.time()

    return render(request, "contact.html", {"form": form})


def _submitted_too_quickly(request):
    minimum = max(0.0, settings.CONTACT_MIN_FILL_SECONDS)
    if minimum == 0:
        return False

    started_at = request.session.get(CONTACT_STARTED_SESSION_KEY)
    if started_at is None:
        return True

    try:
        elapsed = time.time() - float(started_at)
    except (TypeError, ValueError):
        return True

    return elapsed < minimum


def _contact_cache_key(request):
    # The IP is used only to build an in-memory/cache key; it is not saved to
    # ContactMessage. Hashing also keeps the raw address out of cache key names.
    ip = request.META.get("REMOTE_ADDR") or "unknown"
    digest = hashlib.sha256(ip.encode("utf-8")).hexdigest()[:24]
    return f"contact-rate:{digest}"


def _contact_rate_limit_reached(request):
    limit = settings.CONTACT_RATE_LIMIT
    if limit <= 0:
        return False
    return cache.get(_contact_cache_key(request), 0) >= limit


def _record_contact_submission(request):
    limit = settings.CONTACT_RATE_LIMIT
    if limit <= 0:
        return

    key = _contact_cache_key(request)
    timeout = max(1, settings.CONTACT_RATE_WINDOW_SECONDS)

    # add() preserves a fixed window from the first message. incr() is atomic on
    # cache backends that support it; the fallback is enough for a small site.
    if cache.add(key, 1, timeout=timeout):
        return

    try:
        cache.incr(key)
    except (ValueError, NotImplementedError):
        cache.set(key, cache.get(key, 0) + 1, timeout=timeout)


def _send_contact_notification(contact_message):
    """Email the site owner after the message has safely reached the database."""
    if not settings.CONTACT_EMAIL or not settings.EMAIL_HOST_USER:
        return

    try:
        email = EmailMessage(
            # Keep user input out of email headers. Visitor details live in the
            # plain-text body and their validated address is used for Reply-To.
            subject="New message from your website",
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
        # The database copy is already saved, so a temporary SMTP problem never
        # loses the visitor's message.
        logger.exception("Could not send contact-form notification email")

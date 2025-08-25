from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
import environ

env = environ.Env()
environ.Env.read_env()

def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render({},request))


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            full_message = f"From: {name} <{email}>\n\nMessage:\n{message}"

            send_mail(
                subject="New Contact Form Submission",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list= [settings.EMAIL_HOST_USER]
            )

            return render(request, "contact_success.html", {"name": name})
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})   

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
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
            form.save()  #in the db
            return render(request, "contact_success.html", {"name": form.cleaned_data['name']})
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})

def about(request):
    template = loader.get_template('about.html')
    return HttpResponse(template.render({},request))

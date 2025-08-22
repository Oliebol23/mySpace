from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from .models import Member

def home(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render({},request))

def contact(request):
    template = loader.get_template('contact.html')
    return HttpResponse(template.render({},request))

    

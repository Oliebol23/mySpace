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

    
def main(request):
    template = loader.get_template('main.html')
    return HttpResponse(template.render())

def members(request):
    mymembers = Member.objects.all().values()
    template = loader.get_template('all_members.html')
    context = {
        'mymembers':mymembers,
    }
    return HttpResponse(template.render(context, request))

def details(request, id):
    mymember = Member.objects.get(id =id)
    template = loader.get_template('details.html')
    context = {
        'mymember': mymember,
    }
    return HttpResponse(template.render(context, request))





# def deneme():
#     context = {
#         'points: 5'
#     }
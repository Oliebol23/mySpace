from django.contrib import admin
from .models import ContactMessage

# Register your models here.
class MemberAdmin(admin.ModelAdmin):
  admin.site.register(ContactMessage)

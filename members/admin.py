from django.contrib import admin

from .models import ContactMessage, Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("firstname", "lastname", "joined_date")
    search_fields = ("firstname", "lastname")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

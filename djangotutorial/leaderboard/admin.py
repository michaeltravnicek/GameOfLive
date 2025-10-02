from django.contrib import admin
from .models import Event, UserToEvent, ImageToEvent, User


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "date", "place", "points")
    search_fields = ("name", "description")


@admin.register(ImageToEvent)
class ImageToEvent(admin.ModelAdmin):
    list_display = ("event_id", "image")
    search_fields = ("event_id",)

@admin.register(User)
class UserToAdmin(admin.ModelAdmin):
    list_display = ("number", "name")

@admin.register(UserToEvent)
class UserToEventAdmin(admin.ModelAdmin):
    list_display = ("user", "event")
    list_filter = ("event",)
admin.register(Event, UserToEvent)
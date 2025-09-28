from django.contrib import admin
from .models import Event, UserToEvent

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "date", "place", "points", "image")
    search_fields = ("name", "description")

@admin.register(UserToEvent)
class UserToEventAdmin(admin.ModelAdmin):
    list_display = ("user", "event")
    list_filter = ("event",)
admin.register(Event, UserToEvent)
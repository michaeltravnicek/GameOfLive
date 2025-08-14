from django.shortcuts import render
from django.http import HttpResponse
from .models import User
from django.db.models import Count, Sum

def home_view(request):
    leaderboard = (
        User.objects
        .annotate(
            events_count=Count("usertoevent", distinct=True),
            total_points=Sum("usertoevent__event__points")
        )
        .order_by("-total_points") 
    )
    return render(request, "index.html", {"leaderboard": leaderboard})
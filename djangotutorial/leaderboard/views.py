from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import User, UserToEvent, Event
from django.db.models import Count, Sum

def home_view(request):
    return render(request, "welcome.html", {})


def leaderboard_view(request):
    leaderboard = (
        User.objects
        .annotate(
            events_count=Count("usertoevent", distinct=True),
            total_points=Sum("usertoevent__event__points")
        )
        .order_by("-total_points")
    )

    leaderboard_list = list(leaderboard)
    previous_points = None
    rank = 0

    for i, user in enumerate(leaderboard_list, start=1):
        if user.total_points == previous_points:
            user.rank = rank
        else:
            rank = i
            user.rank = rank
            previous_points = user.total_points

    return render(request, "leaderboard.html", {"leaderboard": leaderboard_list})



def user_detail_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    actions = (
        UserToEvent.objects
        .filter(user=user)
        .select_related("event")
        .values("event__name", "event__description", "event__place", "event__date", "event__points")
        .order_by("event__date")
    )

    data = {
        "user_name": user.name,
        "actions": list(actions)
    }
    return JsonResponse(data)


def events_view2(request):
    events = Event.objects.values(
        "id",
        "name",
        "description",
        "place",
        "date",
        "points"
    ).order_by("date")

    data = {
        "events": list(events)
    }
    return render(request, "events.html", {"events": data})

from django.utils import timezone

def events_view(request):
    events = Event.objects.all()
    today = timezone.now().date()

    for event in events:
        if hasattr(event, "date") and event.date:  # pojistka proti null
            event.is_past = event.date.date() < today
        else:
            event.is_past = False

    return render(request, "events.html", {"events": events})



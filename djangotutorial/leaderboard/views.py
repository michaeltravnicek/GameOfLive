from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import User, UserToEvent, Event, ImageToEvent
from django.db.models import Count, Sum
from django.utils import timezone
from .tasks import main, RUN_ALL
from datetime import datetime, timedelta
from django.db.models import F

LAST_UPDATE = None


def home_view(request):
    return render(request, "welcome.html", {})


def leaderboard_view(request):
    global LAST_UPDATE
    global RUN_ALL

    now = datetime.now()

    RUN_ALL = now.hour < LAST_UPDATE.hour if LAST_UPDATE is not None else True
    if LAST_UPDATE is None or datetime.now() - LAST_UPDATE > timedelta(minutes=10):
        main()
        LAST_UPDATE = datetime.now()


    leaderboard = (
        User.objects
        .annotate(
            events_count=Count("usertoevent", distinct=True),
            total_points=Sum("usertoevent__points")
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
        .annotate(user_points=F("points"))
        .values(
            "event__name",
            "event__description",
            "event__place",
            "event__date",
            "user_points"
        )
        .order_by("event__date")
    )

    data = {
        "user_name": user.name,
        "actions": list(actions)
    }
    return JsonResponse(data)


def events_view(request):
    events = Event.objects.all()
    today = timezone.now().date()

    for event in events:
        if hasattr(event, "date") and event.date: 
            event.is_past = event.date.date() < today
        else:
            event.is_past = False

    events = sorted(events, key=lambda e: e.date, reverse=True)
    return render(request, "events.html", {"events": events})


def events_image_views(request, event_id: str):
    event = get_object_or_404(Event, id=event_id)

    images = [
        request.build_absolute_uri(img.image.url)
        for img in ImageToEvent.objects.filter(event_id=event)
        if img.image
    ]

    return JsonResponse({
        "event_id": event_id,
        "images": images
    })
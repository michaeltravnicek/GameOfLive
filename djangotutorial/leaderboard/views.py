from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import User, UserToEvent, Event, ImageToEvent, LastUpdate
from django.db.models import Count, Sum
from django.utils import timezone
from .tasks import main
from datetime import datetime, timedelta, timezone as dt_timezone
from django.db.models import F
from django.utils import timezone
from django.conf import settings

def home_view(request):
    print(settings.MEDIA_ROOT)
    print(settings.MEDIA_URL)
    return render(request, "welcome.html", {})


def leaderboard_view(request):
    last_update_obj = LastUpdate.objects.all().first()
    if last_update_obj is None:
        last_update_obj = LastUpdate.objects.create(
            last_update=datetime.fromtimestamp(0, tz=dt_timezone.utc),  # time -> runs update
            last_complete_update=None
        )

    print("Leaderboard function")
    now = timezone.now() 

    run_all = now.hour < last_update_obj.last_update.hour or last_update_obj.last_complete_update is None
    if now - last_update_obj.last_update > timedelta(minutes=10):
        main(run_all)
        last_update_obj.last_update = now
        if run_all:
            last_update_obj.last_complete_update = now

        last_update_obj.save()

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
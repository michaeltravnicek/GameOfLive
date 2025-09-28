from django.db import models


class Event(models.Model):
    sheet_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, default="Akce")
    description = models.CharField(default="")
    place = models.CharField(max_length=255)
    date = models.DateTimeField()
    points = models.IntegerField()
    image = models.ImageField(upload_to="event_images/", blank=True, null=True)

    def __str__(self):
        return f"{self.sheet_id} - {self.place}"


class User(models.Model):
    name = models.CharField(max_length=255)
    number = models.IntegerField(unique=True)

    def __str__(self):
        return self.name


class UserToEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "event")

    def __str__(self):
        return f"{self.user} → {self.event}"

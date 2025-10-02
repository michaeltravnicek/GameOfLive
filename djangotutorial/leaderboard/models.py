from django.db import models


class Event(models.Model):
    sheet_id = models.CharField(max_length=255)
    sheet_list_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255, default="Akce")
    description = models.CharField(max_length=1023, default="")
    place = models.CharField(max_length=255)
    date = models.DateTimeField()
    points = models.IntegerField()
    image = models.ImageField(upload_to="event_images/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.date} - {self.place} - {self.sheet_id}"
    
    class Meta:
        unique_together = ("sheet_id", "sheet_list_id")


class ImageToEvent(models.Model):
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="event_images/", blank=True, null=True)


class User(models.Model):
    number = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name


class UserToEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    points = models.IntegerField()

    class Meta:
        unique_together = ("user", "event")

    def __str__(self):
        return f"{self.user} → {self.event}"
    
    
class LastUpdate(models.Model):
    last_update = models.DateTimeField(auto_now=True)
    last_complete_update = models.DateTimeField(blank=True, null=True) 
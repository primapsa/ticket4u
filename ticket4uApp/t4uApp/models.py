
from django.utils import timezone
from django.db import models


class Concerts(models.Model):
    title = models.CharField(max_length=100)
    singer = models.CharField(max_length=100)
    ticketsId = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)
    placeId = models.IntegerField(default=0)
    typeId = models.IntegerField(default=0)
    singerVoiceId = models.IntegerField(default=0)
    concertName = models.CharField(max_length=100, null=True)
    composer = models.CharField(max_length=100, null=True)
    wayHint = models.CharField(max_length=100, null=True)
    headliner = models.CharField(max_length=100, null=True)
    censor = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.title

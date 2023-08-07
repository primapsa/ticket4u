from django.db import models


class Concerts(models.Model):
    title = models.CharField(max_length=100)
    singer = models.CharField(max_length=100)
    ticketsID = models.AutoField
    date = models.DateTimeField
    placeId = models.IntegerField
    typeId = models.IntegerField
    singerVoiceId = models.IntegerField
    concertName = models.CharField(max_length=100, null=True)
    composer = models.CharField(max_length=100, null=True)
    wayHint = models.CharField(max_length=100, null=True)
    headliner = models.CharField(max_length=100, null=True)
    censor = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.title

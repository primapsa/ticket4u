from django.utils import timezone
from django.db import models


class Concerts(models.Model):
    title = models.CharField(max_length=100)
    singer = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    placeId = models.IntegerField()
    typeId = models.IntegerField()
    singerVoiceId = models.IntegerField(default=0)
    concertName = models.CharField(max_length=100, null=True)
    composer = models.CharField(max_length=100, null=True)
    wayHint = models.CharField(max_length=100, null=True)
    headliner = models.CharField(max_length=100, null=True)
    censor = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.title


class Tickets(models.Model):
    concertId = models.IntegerField()
    userId = models.IntegerField(default=0)
    statusId = models.IntegerField(default=0)
    promocodeId = models.IntegerField(default=0)
    price = models.FloatField()
    finalPrice = models.FloatField()


class Place(models.Model):
    title = models.CharField(max_length=100)
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)


class ConcertType(models.Model):
    title = models.CharField(max_length=100)


class SingerVoice(models.Model):
    title = models.CharField(max_length=100)


class TicketStatus(models.Model):
    title = models.CharField(max_length=100)


class Cart(models.Model):
    userId = models.IntegerField()
    ticketId = models.IntegerField()


class Promocode(models.Model):
    title = models.CharField(max_length=100)
    concertId = models.IntegerField()
    discount = models.IntegerField()





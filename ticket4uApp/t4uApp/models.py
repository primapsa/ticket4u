from django.utils import timezone
from django.db import models


class ConcertType(models.Model):
    title = models.CharField(max_length=100)


class Concerts(models.Model):
    title = models.CharField(max_length=100)
    singer = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    placeId = models.IntegerField(default=0)
    typeId = models.ForeignKey(ConcertType, default=0, on_delete=models.SET_DEFAULT, related_name='types')
    singerVoiceId = models.IntegerField(default=0)
    concertName = models.CharField(max_length=100, null=True)
    composer = models.CharField(max_length=100, null=True)
    wayHint = models.CharField(max_length=100, null=True)
    headliner = models.CharField(max_length=100, null=True)
    censor = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.title


class TicketStatus(models.Model):
    title = models.CharField(max_length=100)


class Promocode(models.Model):
    title = models.CharField(max_length=100)
    concertId = models.IntegerField()
    discount = models.IntegerField()


class Tickets(models.Model):
    concertId = models.ForeignKey(Concerts, on_delete=models.CASCADE, null=False)
    userId = models.IntegerField(default=0)
    statusId = models.ForeignKey(TicketStatus, default=1, on_delete=models.SET_DEFAULT)
    promocodeId = models.ForeignKey(Promocode, default=1, on_delete=models.SET_DEFAULT)

    price = models.FloatField()
    finalPrice = models.FloatField()


class Place(models.Model):
    title = models.CharField(max_length=100)
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)


class SingerVoice(models.Model):
    title = models.CharField(max_length=100)


class Cart(models.Model):
    userId = models.IntegerField()
    ticketId = models.IntegerField()

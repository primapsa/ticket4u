from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from t4uApp.utils import upload_to
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User

class ConcertType(models.Model):
    title = models.CharField(max_length=100)


class Place(models.Model):
    address = models.CharField(max_length=100, null=True)
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)


class SingerVoice(models.Model):
    title = models.CharField(max_length=100)


class Concerts(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    placeId = models.ForeignKey(
        Place, blank=True, null=True, default=None, on_delete=models.SET_DEFAULT
    )
    typeId = models.ForeignKey(
        ConcertType, blank=True, null=True, default=None, on_delete=models.SET_DEFAULT
    )
    singerVoiceId = models.ForeignKey(
        SingerVoice, blank=True, null=True, default=None, on_delete=models.SET_DEFAULT
    )
    concertName = models.CharField(max_length=100, null=True, blank=True)
    composer = models.CharField(max_length=100, null=True, blank=True)
    wayHint = models.CharField(max_length=100, null=True, blank=True)
    headliner = models.CharField(max_length=100, null=True, blank=True)
    censor = models.CharField(max_length=100, null=True, blank=True)
    poster = models.FileField(
        default="no_image.png",
        upload_to=upload_to,
        validators=[FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg"])],
    )
    desc = models.CharField(max_length=15000, null=True, blank=True)
    price = models.IntegerField(default=0)
    ticket = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class TicketStatus(models.Model):
    title = models.CharField(max_length=100)


class Promocode(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    discount = models.IntegerField(
        validators=[MaxValueValidator(99), MinValueValidator(0)],
    )


class Tickets(models.Model):
    concert = models.ForeignKey(Concerts, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE )
    status = models.ForeignKey(TicketStatus, blank=True, null=True, default=None, on_delete=models.SET_DEFAULT)
    count = models.IntegerField(default=1)
  


class Cart(models.Model):
    userId = models.IntegerField()
    concertId = models.ForeignKey(
        Concerts, blank=True, default=0, on_delete=models.CASCADE
    )
    count = models.IntegerField(default=1)
    promocodeId = models.ForeignKey(
        Promocode, blank=True, null=True, default=None, on_delete=models.SET_DEFAULT
    )
    price = models.FloatField(default=0)
    statusId = models.IntegerField(default=1)


@receiver(post_delete, sender=Concerts)
def post_save_image(sender, instance, *args, **kwargs):
    try:
        instance.poster.delete(save=False)
    except:
        pass

from django.db import models
from django.utils import timezone
from t4uApp.utils import upload_to
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.core.validators import FileExtensionValidator


class ConcertType(models.Model):
    title = models.CharField(max_length=100)


class Place(models.Model):
    address = models.CharField(max_length=100, default='')
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)


class Concert(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    place = models.ForeignKey(Place, null=True, on_delete=models.SET_NULL)
    type = models.ForeignKey(ConcertType, null=True, on_delete=models.SET_NULL)
    poster = models.FileField(
        upload_to=upload_to,
        validators=[FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg"])],)
    desc = models.CharField(max_length=15000, null=True, blank=True)
    price = models.IntegerField(default=0)
    ticket = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Party(Concert):
    censor = models.CharField(max_length=100)


class Openair(Concert):
    wayHint = models.CharField(max_length=100)
    headliner = models.CharField(max_length=100)


class SingerVoice(models.Model):
    title = models.CharField(max_length=100)


class Classic(Concert):
    singerVoice = models.ForeignKey(SingerVoice, null=True, on_delete=models.SET_NULL)
    concertName = models.CharField(max_length=100)
    composer = models.CharField(max_length=100)


@receiver(post_delete, sender=Concert)
def post_save_image(sender, instance, *args, **kwargs):
    try:
        instance.poster.delete(save=False)
    except:
        pass

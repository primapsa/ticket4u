from django.db import models
from django.utils import timezone
from t4uApp.utils import upload_to
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.core.validators import FileExtensionValidator


class ConcertType(models.Model):
    title = models.CharField(max_length=100)


class Place(models.Model):
    address = models.CharField(max_length=100, null=True)
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)


class SingerVoice(models.Model):
    title = models.CharField(max_length=100)

class ConcertParty(models.Model):
    censor = models.CharField(max_length=100)

class ConcertOpenair(models.Model):
    wayHint = models.CharField(max_length=100)
    headliner = models.CharField(max_length=100)

class ConcertClassic(models.Model):
    singerVoiceId = models.ForeignKey(SingerVoice, on_delete=models.CASCADE)
    concertName = models.CharField(max_length=100)
    composer = models.CharField(max_length=100)

class ConcertExtra(models.Model):
    party = models.ForeignKey(ConcertParty, blank=True, null=True, default=None, on_delete=models.SET_DEFAULT)
    openair = models.ForeignKey(ConcertOpenair, blank=True, null=True, default=None, on_delete=models.SET_DEFAULT)
    classic = models.ForeignKey(ConcertClassic, blank=True, null=True, default=None, on_delete=models.SET_DEFAULT)
    
class Concerts(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    placeId = models.ForeignKey(
        Place, blank=True, null=True, default=None, on_delete=models.SET_DEFAULT
    )
    typeId = models.ForeignKey(
        ConcertType, blank=True, null=True, default=None, on_delete=models.SET_DEFAULT
    )    
    poster = models.FileField(
        default="no_image.png",
        upload_to=upload_to,
        validators=[FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg"])],
    )
    desc = models.CharField(max_length=15000, null=True, blank=True)
    price = models.IntegerField(default=0)
    ticket = models.IntegerField(default=0)
    extra = models.ForeignKey(ConcertExtra, default=None, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
@receiver(post_delete, sender=Concerts)
def post_save_image(sender, instance, *args, **kwargs):
    try:
        instance.poster.delete(save=False)
    except:
        pass
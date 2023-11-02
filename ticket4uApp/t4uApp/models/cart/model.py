from django.db import models
from ..concert import Concerts
from ..promocode import Promocode

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
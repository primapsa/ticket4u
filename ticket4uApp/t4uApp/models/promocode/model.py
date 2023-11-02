from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

class Promocode(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    discount = models.IntegerField(
        validators=[MaxValueValidator(99), MinValueValidator(0)],
    )

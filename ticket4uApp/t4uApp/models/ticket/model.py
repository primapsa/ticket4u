from django.db import models
from django.contrib.auth.models import User
from ..concert import Concert


class TicketStatus(models.Model):
    title = models.CharField(max_length=100)

class Tickets(models.Model):
    concert = models.ForeignKey(Concert, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE )
    status = models.ForeignKey(TicketStatus, blank=True, null=True, default=None, on_delete=models.SET_DEFAULT)
    count = models.IntegerField(default=1)  

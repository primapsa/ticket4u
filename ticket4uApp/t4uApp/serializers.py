from rest_framework import serializers
from .models import Concerts


class ConcertsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concerts
        fields = ('id', 'title', 'singer', 'ticketsId', 'date', 'placeId', 'typeId', 'singerVoiceId', 'concertName',
                  'composer', 'wayHint', 'headliner', 'censor')

from rest_framework import serializers
from .models import Concerts, Place, ConcertType, SingerVoice


class ConcertsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concerts
        fields = '__all__'


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ('title', 'latitude', 'longitude')


class ConcertsExtendedSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()
    price = serializers.FloatField()
    tickets = serializers.IntegerField()

    class Meta:
        model = Concerts
        fields = ('title', 'singer', 'placeId', 'typeId', 'place', 'price', 'tickets')


class ConcertTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConcertType
        fields = '__all__'

class SingerVoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingerVoice
        fields = '__all__'

class CartSerializer(seria)
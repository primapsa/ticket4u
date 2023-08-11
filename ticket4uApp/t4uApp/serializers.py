from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Concerts, Place, ConcertType, SingerVoice, Cart, Promocode


class ConcertTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConcertType
        fields = '__all__'


class ConcertsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concerts
        fields = '__all__'


class ConcertsSerializerEx(serializers.ModelSerializer):
    type = serializers.CharField(source='typeId__title')
    latitude = serializers.CharField(source='placeId__latitude')
    longitude = serializers.CharField(source='placeId__longitude')
    voice = serializers.CharField(source='singerVoiceId__title')

    class Meta:
        model = Concerts
        fields = ('id', 'title', 'singer', 'concertName', 'composer',
                  'wayHint', 'headliner', 'censor', 'date', 'latitude', 'longitude', 'type', 'voice')


class ConcertsSerializerOutput(serializers.Serializer):
    data = ConcertsSerializerEx()
    results = serializers.IntegerField()

    # class Meta:
    #     fields = ('data', 'results')


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


class SingerVoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingerVoice
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class PromocodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocode
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

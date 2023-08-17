from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Concerts, Place, ConcertType, SingerVoice, Cart, Promocode


class ConcertTypeSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='id')
    label = serializers.CharField(source='title')

    class Meta:
        model = ConcertType
        fields = ('value', 'label')


class ConcertsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concerts
        fields = '__all__'


class ConcertsSerializerEx(serializers.ModelSerializer):
    type = serializers.CharField(source='typeId__title')
    address = serializers.CharField(source='placeId__address')
    latitude = serializers.CharField(source='placeId__latitude')
    longitude = serializers.CharField(source='placeId__longitude')
    voice = serializers.CharField(source='singerVoiceId__title')

    class Meta:
        model = Concerts
        fields = ('id', 'title', 'concertName', 'composer',
                  'wayHint', 'headliner', 'censor', 'date', 'address', 'latitude', 'longitude', 'type', 'voice')


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ('address', 'latitude', 'longitude')


class ConcertsExtendedSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()
    price = serializers.FloatField()
    tickets = serializers.IntegerField()

    class Meta:
        model = Concerts
        fields = ('title', 'date', 'typeId', 'singerVoiceId', 'concertName',
                  'composer', 'wayHint', 'headliner', 'censor', 'place', 'poster', 'price', 'tickets')


class ConcertsExtendedSerializer2(serializers.ModelSerializer):
    price = serializers.FloatField()
    tickets = serializers.IntegerField()
    address = serializers.CharField(max_length=100)
    latitude = serializers.CharField(max_length=100)
    longitude = serializers.CharField(max_length=100)

    class Meta:
        model = Concerts
        fields = ('title', 'date', 'typeId', 'singerVoiceId', 'concertName',
                  'composer', 'wayHint', 'headliner', 'censor', 'address','latitude','longitude', 'poster', 'price', 'tickets')


class SingerVoiceSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='id')
    label = serializers.CharField(source='title')

    class Meta:
        model = SingerVoice
        fields = ('value', 'label')


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

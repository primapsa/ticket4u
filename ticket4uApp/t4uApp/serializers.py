from django.contrib.auth.models import User
# from .models import User
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
    poster = serializers.CharField()

    class Meta:
        model = Concerts
        fields = ('id', 'title', 'concertName', 'composer', 'wayHint', 'headliner', 'censor',
                  'date', 'address', 'latitude', 'longitude', 'type', 'typeId_id', 'voice', 'singerVoiceId_id',
                  'poster')


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
                  'composer', 'wayHint', 'headliner', 'censor', 'address', 'latitude', 'longitude', 'poster', 'price',
                  'tickets')


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


class CartSerializerEx(serializers.ModelSerializer):
    title = serializers.CharField(source='concertId__title')
    poster = serializers.CharField(source='concertId__poster')
    price = serializers.IntegerField(source='concertId__price')
    tickets = serializers.IntegerField(source='concertId__ticket')
    discount = serializers.IntegerField(source='promocodeId__discount')
    promocode = serializers.CharField(source='promocodeId__title')

    class Meta:
        model = Cart
        fields = ('id', 'count', 'title', 'poster', 'price', 'tickets', 'discount', 'promocode')


class PromocodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocode
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'token']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)






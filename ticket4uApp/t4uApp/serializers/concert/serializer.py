from rest_framework import serializers
from t4uApp.models.models import Concerts, Place, ConcertType, SingerVoice


class ConcertTypeSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='id')
    label = serializers.CharField(source='title')

    class Meta:
        model = ConcertType
        fields = ('value', 'label')


class ConcertsTypePlaceSingerSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(source='typeId.title')
    address = serializers.ReadOnlyField(source='placeId.address')
    latitude = serializers.ReadOnlyField(source='placeId.latitude')
    longitude = serializers.ReadOnlyField(source='placeId.longitude')
    voice = serializers.ReadOnlyField(source='singerVoiceId.title')
    poster = serializers.FileField(use_url = False)
    ticket_limit = serializers.SerializerMethodField()

    class Meta:
        model = Concerts
        fields = ('id', 'title', 'concertName', 'composer', 'wayHint', 'headliner', 'censor',
                  'date', 'address', 'latitude', 'longitude', 'type', 'typeId_id', 'voice', 'singerVoiceId_id',
                  'poster', 'price', 'ticket', 'desc', 'ticket_limit') 
         
    def get_ticket_limit(self, obj):
        # tickets = Tickets.objects.filter(concert=obj)
        tickets = []
        count_sum = sum(ticket.count for ticket in tickets)
        return int(obj.ticket - count_sum)
 

# class TicketsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tickets
#         fields = ('price',)

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
                  'poster', 'price', 'ticket', 'desc')


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
        

class ConcertsAddresSerializer(serializers.ModelSerializer):
    price = serializers.FloatField()
    ticket = serializers.IntegerField()
    address = serializers.CharField(max_length=100)
    latitude = serializers.CharField(max_length=100)
    longitude = serializers.CharField(max_length=100)

    class Meta:
        model = Concerts
        fields = ('title', 'date', 'typeId', 'singerVoiceId', 'concertName',
                  'composer', 'wayHint', 'headliner', 'censor', 'address', 'latitude', 'longitude', 'poster', 'price',
                  'ticket')
        
        
class SingerVoiceSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='id')
    label = serializers.CharField(source='title')

    class Meta:
        model = SingerVoice
        fields = ('value', 'label')
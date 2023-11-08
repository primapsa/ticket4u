from rest_framework import serializers
from t4uApp.models import (
    Concerts,
    Place,
    ConcertType,
    SingerVoice,
    Tickets,
    ConcertParty,
    ConcertOpenair,
    ConcertClassic
)


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ('address', 'latitude', 'longitude')


class ConcertTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConcertType
        fields = ('id','title' )
        read_only_field = ('id', )

# class ConcertTypeWithoutTitle(ConcertTypeSerializer):
#     class Meta(ConcertTypeSerializer.Meta):
#        fields = ('id', )

class ConcertsSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()  
    poster = serializers.FileField(use_url=False) 

    class Meta:
        model = Concerts
        fields = ('id', 'title', 'date', 'type', 'poster', 'desc', 'price', 'ticket', 'place')
        
# class ConcertWithoutFieldsSerializer(ConcertsSerializer):
#      class Meta(ConcertsSerializer.Meta):
#        fields = ('title', 'date', 'desc', 'price', 'ticket')




class BaseConcertExtraSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()
    class Meta:
        model = Place
        fields = '__all__'
        read_only_fields = ('id', )

    def create(self, validated):
        place_data = validated.pop('place')
        place = Place.objects.create(**place_data)
        concert_extra = self.Meta.model.objects.create(**validated, place=place)
        return concert_extra
    
class ConcertClassicSerializer(BaseConcertExtraSerializer):
    class Meta:
        model = ConcertClassic
        fields = ConcertsSerializer.Meta.fields + ('singerVoice', 'concertName', 'composer')

class ConcertPartySerializer(BaseConcertExtraSerializer):  

    class Meta:
        model = ConcertParty
        fields = ConcertsSerializer.Meta.fields + ('censor', )
      
class ConcertOpenairSerializer(BaseConcertExtraSerializer):
    class Meta:
        model = ConcertOpenair
        fields = ConcertsSerializer.Meta.fields + ('wayHint', 'headliner')

# class ConcertPartyOutputSerializer(ConcertsSerializer):
#         place = PlaceSerializer(read_only=True)  # Вложенный сериализатор для Place
#         class Meta:
#             model = ConcertParty
#             fields = '__all__'




class ConcertsTypePlaceSingerSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(source="typeId.title")
    address = serializers.ReadOnlyField(source="placeId.address")
    latitude = serializers.ReadOnlyField(source="placeId.latitude")
    longitude = serializers.ReadOnlyField(source="placeId.longitude")
    voice = serializers.ReadOnlyField(source="extra.classic.singerVoiceId.title")
    singerVoiceId = serializers.ReadOnlyField(source="extra.classic.singerVoiceId_id")
    concertName = serializers.ReadOnlyField(source="extra.classic.concertName")
    composer = serializers.ReadOnlyField(source="extra.classic.composer")
    wayHint = serializers.ReadOnlyField(source="extra.openair.wayHint")
    headliner = serializers.ReadOnlyField(source="extra.openair.headliner")
    censor = serializers.ReadOnlyField(source="extra.party.censor")
    poster = serializers.FileField(use_url=False)
    ticket_limit = serializers.SerializerMethodField()

    class Meta:
        model = Concerts
        fields = (
            "id",
            "title",
            "date",
            "address",
            "latitude",
            "longitude",
            "type",
            "typeId_id",
            "voice",
            "singerVoiceId",
            "concertName",
            "composer",
            "wayHint",
            "headliner",
            "censor",
            "poster",
            "price",
            "ticket",
            "desc",
            "ticket_limit",
        )

    def get_ticket_limit(self, obj):
        tickets = Tickets.objects.filter(concert=obj)
        count_sum = sum(ticket.count for ticket in tickets)
        return int(obj.ticket - count_sum)


class ConcertsUpdateSerializer(ConcertsTypePlaceSingerSerializer):
    class Meta:
        model = Concerts
        fields = (
            "id",
            "title",
            "date",
            "address",
            "latitude",
            "longitude",
            "type",
            "typeId",
            "voice",
            "singerVoiceId",
            "concertName",
            "composer",
            "wayHint",
            "headliner",
            "censor",
            "poster",
            "price",
            "ticket",
            "desc",
            "ticket_limit",
            "placeId",
        )


class TicketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tickets
        fields = ("price",)


# class ConcertsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Concerts
#         fields = "__all__"


class ConcertsSerializerEx(serializers.ModelSerializer):
    type = serializers.CharField(source="typeId__title")
    address = serializers.CharField(source="placeId__address")
    latitude = serializers.CharField(source="placeId__latitude")
    longitude = serializers.CharField(source="placeId__longitude")
    voice = serializers.CharField(source="singerVoiceId__title")
    poster = serializers.CharField()

    class Meta:
        model = Concerts
        fields = (
            "id",
            "title",
            "concertName",
            "composer",
            "wayHint",
            "headliner",
            "censor",
            "date",
            "address",
            "latitude",
            "longitude",
            "type",
            "typeId_id",
            "voice",
            "singerVoiceId_id",
            "poster",
            "price",
            "ticket",
            "desc",
        )


class ConcertsExtendedSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()
    price = serializers.FloatField()
    tickets = serializers.IntegerField()

    class Meta:
        model = Concerts
        fields = (
            "title",
            "date",
            "typeId",
            "singerVoiceId",
            "concertName",
            "composer",
            "wayHint",
            "headliner",
            "censor",
            "place",
            "poster",
            "price",
            "tickets",
        )


class ConcertsAddresSerializer(serializers.ModelSerializer):
    price = serializers.FloatField()
    ticket = serializers.IntegerField()
    address = serializers.CharField(max_length=100)
    latitude = serializers.CharField(max_length=100)
    longitude = serializers.CharField(max_length=100)

    class Meta:
        model = Concerts
        fields = (
            "title",
            "date",
            "typeId",
            "address",
            "latitude",
            "longitude",
            "poster",
            "price",
            "ticket",
        )


class SingerVoiceSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source="id")
    label = serializers.CharField(source="title")

    class Meta:
        model = SingerVoice
        fields = ("value", "label")

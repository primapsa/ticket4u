from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from t4uApp.models import (
    Concert,
    Place,
    ConcertType,
    SingerVoice,
    Tickets,
    Party,
    Openair,
    Classic
)


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ('address', 'latitude', 'longitude')


class ConcertTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConcertType
        fields = ('id', 'title')
        read_only_field = ('id',)


class ConcertsSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()
    poster = serializers.FileField(use_url=False)

    class Meta:
        model = Concert
        fields = ('id', 'title', 'date', 'type', 'poster', 'desc', 'price', 'ticket', 'place')


class ConcertsWithRelativesSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()
    poster = serializers.FileField(use_url=False)
    ticket_limit = serializers.SerializerMethodField()

    class Meta:
        model = Concert
        fields = '__all__'

    def to_representation(self, instance):
        output = super().to_representation(instance)
        concert_type = instance.type_id

        if concert_type == 1:
            concert_classic_data = ConcertClassicSerializer(instance.classic).data
            output.update({
                'concertName': concert_classic_data.get('concertName', None),
                'composer': concert_classic_data.get('composer', None),
                'singerVoice': str(instance.concertclassic.singerVoice_id),
            })
        elif concert_type == 2:
            concert_party_data = ConcertPartySerializer(instance.party).data
            output.update(concert_party_data)
        elif concert_type == 3:
            concert_openair_data = ConcertOpenairSerializer(instance.openair).data
            output.update(concert_openair_data)
        return output

    def get_ticket_limit(self, obj):
        tickets = Tickets.objects.filter(concert=obj)
        count_sum = sum(ticket.count for ticket in tickets)
        return int(obj.ticket - count_sum)


class BaseConcertExtraSerializer(serializers.ModelSerializer):
    place = PlaceSerializer()
    poster = serializers.FileField(use_url=False,
                                   validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], )

    class Meta:
        model = Place
        fields = '__all__'
        read_only_fields = ('id', 'type',)

    def create(self, validated):
        place_data = validated.pop('place')
        place = Place.objects.create(**place_data)
        concert_extra = self.Meta.model.objects.create(**validated, place=place)
        return concert_extra

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['place'] = PlaceSerializer(instance.place).data
        return representation

    def update(self, instance, validated):
        place_data = validated.pop('place')
        if place_data:
            place = Place.objects.get(id=instance.place.id)
            updated_place = PlaceSerializer(place, place_data)
            if updated_place.is_valid():
                updated_place.save()

        for attr, value in validated.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class SingerVoiceSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source="id")
    label = serializers.CharField(source="title")

    class Meta:
        model = SingerVoice
        fields = ("value", "label")
        fields_read_only = ("value", "label")


class ConcertClassicSerializer(BaseConcertExtraSerializer):
    class Meta:
        model = Classic
        fields = ConcertsSerializer.Meta.fields + ('singerVoice', 'concertName', 'composer')


class ConcertPartySerializer(BaseConcertExtraSerializer):
    class Meta:
        model = Party
        fields = ConcertsSerializer.Meta.fields + ('censor',)


class ConcertOpenairSerializer(BaseConcertExtraSerializer):
    class Meta:
        model = Openair
        fields = ConcertsSerializer.Meta.fields + ('wayHint', 'headliner')


class TicketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tickets
        fields = ("price",)

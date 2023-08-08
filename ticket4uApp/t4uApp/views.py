from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework import status

from .models import Concerts, Tickets
from .serializers import *
from .utils import make_bulk


@api_view(['GET', 'POST'])
def concert_list(request):
    # print(request)
    # myr = request.data
    # pl = myr.pop('place')
    # return Response([pl,myr] )
    if request.method == 'GET':
        data = Concerts.objects.all()
        serializer = ConcertsSerializer(data, context={'request': request}, many=True)
        return Response(serializer.data)

    if request.method == 'POST':

        serializer = ConcertsExtendedSerializer(data=request.data)
        if serializer.is_valid():
            concerts = request.data
            place = concerts.pop('place')
            place_serializer = PlaceSerializer(data=place)
            if place_serializer.is_valid():
                place_result = place_serializer.save()
                concerts['placeId'] = place_result.pk
                concerts_serializer = ConcertsSerializer(data=concerts)
                if concerts_serializer.is_valid():
                    result_concerts = concerts_serializer.save()
                    tickets = make_bulk(int(concerts['tickets']),
                                        Tickets(concertId=result_concerts.pk, price=concerts['price'],
                                                finalPrice=concerts['price']))
                    Tickets.objects.bulk_create(tickets)
                    return Response(concerts_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(concerts_serializer.errors, status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def concert_type(request):
    data = ConcertType.objects.all()
    serializer = ConcertTypeSerializer(data, context={'request': request}, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def singer_voice(request):
    data = SingerVoice.objects.all()
    serializer = SingerVoiceSerializer(data, context={'request': request}, many=True)
    return Response(serializer.data)


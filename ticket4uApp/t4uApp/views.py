from django.db import connection
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core import serializers as ssrs
from rest_framework import status

from .models import Concerts, Tickets, ConcertType
from .serializers import *
from .utils import make_bulk
from django.http import JsonResponse


@api_view(['GET'])
def concert_filter(request):
    search = request.GET.get('q')
    data = (Concerts.objects.filter(title__startswith=search).select_related('typeId', 'placeId', 'singerVoiceId')
            .values('singer', 'title', 'date', 'typeId__title', 'placeId__latitude', 'placeId__longitude',
                    'singerVoiceId__title'))
    serializer = ConcertsSerializerEx(data, context={'request': request}, many=True)
    return Response(serializer.data, status.HTTP_200_OK)



@api_view(['GET', 'POST'])
def concert_list(request):
    # print(request)
    # myr = request.data
    # pl = myr.pop('place')
    # return Response([pl,myr] )
    if request.method == 'GET':
        # data = Concerts.objects.all()
        # data = Concerts.objects.all().values_list('singer').union(ConcertType.objects.all().values_list('title'))
        # dt = Concerts.objects.select_related('typeId')
        # print (type (dt))
        # concert_obj = {}
        # concert_list = []
        # for record in dt:
        #     obj = record.copy()
        # print(record.singer, record.title, record.typeId.title)
        data = (Concerts.objects.select_related('typeId', 'placeId', 'singerVoiceId')
                .values('singer', 'title', 'date', 'typeId__title', 'placeId__latitude', 'placeId__longitude',
                        'singerVoiceId__title'))
        # print(data[0])
        # print(connection.queries)
        # print(data[0].singer)
        # serializers.serialize('json',  Car.objects.all().select_related('dealership'))
        serializer = ConcertsSerializerEx(data, context={'request': request}, many=True)
        # return JsonResponse(data, safe=False)
        return Response(serializer.data, status.HTTP_200_OK)
        # return Response(ssrs.serialize('json', Concerts.objects.select_related('typeId').filter(id=1)))
        # return Response('11')

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
                                        Tickets(concertId=result_concerts, price=concerts['price'],
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
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
def singer_voice(request):
    data = SingerVoice.objects.all()
    serializer = SingerVoiceSerializer(data, context={'request': request}, many=True)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def cart_list(request):
    if request.method == 'GET':
        data = Cart.objects.all()
        serializer = CartSerializer(data, context={'request': request}, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
    if request.method == 'POST':
        serializer = ConcertsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
def cart_change(request, pk):
    try:
        record = Cart.objects.get(pk=pk)
    except:
        return Response(status.HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        record.delete()
        return Response(status.HTTP_204_NO_CONTENT)
    if request.method == 'PUT':
        serializer = CartSerializer(record, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def promocode_list(request):
    if request.method == 'GET':
        promocodes = Promocode.objects.all()
        serializer = PromocodeSerializer(promocodes, context={'request': request}, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    if request.method == 'POST':
        serializer = PromocodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
def promocode_change(request, pk):
    try:
        record = Promocode.objects.get(pk=pk)
    except:
        return Response(status.HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        record.delete()
        return Response(status.HTTP_204_NO_CONTENT)
    if request.method == 'PUT':
        serializer = PromocodeSerializer(record, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user(request):
    return Response(request.user)

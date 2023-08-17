from rest_framework.response import Response
from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Tickets
from .serializers import *
from .setting import page
from .utils import make_bulk


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
        per_page = request.GET.get("count") or page['itemsPerPage']
        page_number = request.GET.get("page") or page['default']
        keyword = request.GET.get("keyword") or ''

        concerts = (
            Concerts.objects.filter(title__startswith=keyword).select_related('typeId', 'placeId', 'singerVoiceId')
            .values('id', 'title', 'date', 'typeId__title', 'placeId__address', 'placeId__latitude',
                    'placeId__longitude',
                    'singerVoiceId__title'))

        paginator = Paginator(concerts, per_page)
        paged_concert = paginator.get_page(page_number)
        # print(data[0])
        # print(connection.queries)
        # print(data[0].singer)
        # serializers.serialize('json',  Car.objects.all().select_related('dealership'))

        serializer = ConcertsSerializerEx(paged_concert, context={'request': request}, many=True)
        output = {'data': serializer.data, 'total': concerts.count()}
        return Response(output, status.HTTP_200_OK)
        # return Response(ssrs.serialize('json', Concerts.objects.select_related('typeId').filter(id=1)))
        # return Response('11')

    if request.method == 'POST':

        # serializer = ConcertsExtendedSerializer2(data=request.data)
        # if serializer.is_valid():
        #     concerts = request.data
        #     place = concerts.pop('place')
        #     place_serializer = PlaceSerializer(data=place)
        #     if place_serializer.is_valid():
        #         place_result = place_serializer.save()
        #         concerts['placeId'] = place_result.pk
        #         concerts_serializer = ConcertsSerializer(data=concerts)
        #         if concerts_serializer.is_valid():
        #             result_concerts = concerts_serializer.save()
        #             tickets = make_bulk(int(concerts['tickets']),
        #                                 Tickets(concertId=result_concerts, price=concerts['price'],
        #                                         finalPrice=concerts['price']))
        #             Tickets.objects.bulk_create(tickets)
        #             return Response(concerts_serializer.data, status=status.HTTP_201_CREATED)
        #         else:
        #             return Response(concerts_serializer.errors, status.HTTP_400_BAD_REQUEST)
        serializer = ConcertsExtendedSerializer2(data=request.data)
        print(request.data)
        if serializer.is_valid():
            concerts = request.data.copy()
            # place = concerts.pop('place')
            print('step1')
            new_place = {'address': concerts['address'], 'latitude': concerts['latitude'],
                         'longitude': concerts['longitude']}
            # qdict = QueryDict('', mutable=True)
            # qdict.update(MultiValueDict(new_place))
            # print(qdict['address'])
            place_serializer = PlaceSerializer(data=new_place)
            if place_serializer.is_valid():
                print('step2')
                place_result = place_serializer.save()
                concerts['placeId'] = place_result.pk
                concerts_serializer = ConcertsSerializer(data=concerts)
                if concerts_serializer.is_valid():
                    print('step3')
                    result_concerts = concerts_serializer.save()
                    tickets = make_bulk(int(concerts['tickets']),
                                        Tickets(concertId=result_concerts, price=concerts['price'],
                                                finalPrice=concerts['price']))
                    Tickets.objects.bulk_create(tickets)
                    return Response(concerts_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(concerts_serializer.errors, status.HTTP_400_BAD_REQUEST)
        print(serializer.errors)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE', 'GET'])
def concert(request, pk):
    try:
        record = Concerts.objects.get(pk=pk)
    except:
        return Response(status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        record.delete()
        return Response(status.HTTP_204_NO_CONTENT)
    if request.method == 'PUT':
        serializer = ConcertsExtendedSerializer(record, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        concert = (
            Concerts.objects.filter(id=pk).select_related('typeId', 'placeId', 'singerVoiceId')
            .values('id', 'title', 'date', 'placeId__address', 'typeId__title', 'placeId__latitude',
                    'placeId__longitude',
                    'singerVoiceId__title'))
        serializer = ConcertsSerializerEx(concert, context={'request': request}, many=True)
        return Response(serializer.data, status.HTTP_200_OK)


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
        output = {'data': serializer.data, 'total': promocodes.count()}
        return Response(output, status.HTTP_200_OK)

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

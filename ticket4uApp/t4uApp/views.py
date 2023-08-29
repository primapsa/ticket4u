import base64
import json
import uuid

from django.core.paginator import Paginator
from django.db.models import F
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
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
        type = request.GET.get("type") or 0
        ids = request.GET.get("ids") or ''

        concerts = (
            Concerts.objects.filter(title__icontains=keyword).select_related('typeId', 'placeId', 'singerVoiceId')
            .values('id', 'title', 'date', 'placeId__address', 'typeId_id', 'typeId__title', 'placeId__latitude',
                    'placeId__longitude', 'singerVoiceId__title', 'singerVoiceId_id', 'poster', 'censor'))
        # print(Concerts.Tickets_set.all())
        if int(type) > 0:
            concerts = concerts.filter(typeId_id=type)
        if ids:
            ids_tuple = tuple(map(int, ids.split(',')))
            concerts = concerts.filter(id__in=ids_tuple)
        paginator = Paginator(concerts, per_page)
        paged_concert = paginator.get_page(page_number)
        # print(data[0])
        # print(connection.queries)

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
            new_place = {'address': concerts['address'], 'latitude': concerts['latitude'],
                         'longitude': concerts['longitude']}
            # qdict = QueryDict('', mutable=True)
            # qdict.update(MultiValueDict(new_place))
            # print(qdict['address'])
            place_serializer = PlaceSerializer(data=new_place)
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
            .values('id', 'title', 'date', 'placeId__address', 'typeId_id', 'typeId__title', 'placeId__latitude',
                    'placeId__longitude', 'singerVoiceId__title', 'singerVoiceId_id', 'poster'))
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
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE', 'GET'])
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


@api_view(['GET'])
def cart_user(request, uid):
    try:
        record = (Cart.objects.filter(userId=uid).select_related('concertId', 'promocodeId')
                  .values('id', 'count', 'concertId__title', 'concertId__poster',
                          'concertId__price', 'concertId__ticket', 'promocodeId__discount', 'promocodeId__title'))
    except:
        return Response(status.HTTP_404_NOT_FOUND)
    serializer = CartSerializerEx(record, context={'request': request}, many=True)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes((permissions.IsAuthenticated, permissions.IsAdminUser))
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


@api_view(['POST'])
def promocode_find(request):
    promocode = request.data
    if not promocode:
        return Response('',status.HTTP_400_BAD_REQUEST)
    result = Promocode.objects.filter(title=promocode['promocode']).values()
    if not (len(result)):
        return Response(0,status.HTTP_200_OK)
    result = result[0]
    id = result['id']
    title = result['title']
    discount = result['discount']
    cart = Cart.objects.filter(id=promocode['id']).update(promocodeId=id)
    if cart:
        output = {'cartId': promocode['id'], 'title': title, 'discount': discount }
        return Response(output, status.HTTP_200_OK)
    return Response(status.HTTP_400_BAD_REQUEST)




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


@api_view(['POST'])
def paypal(request):
    if not request.data:
        return Response(status.HTTP_400_BAD_REQUEST)
    ids_decoded = request.data['resource']['purchase_units'][0]['reference_id']
    # pay_status = request.data['status']
    # if not pay_status == 'APPROVED':
    #     return Response(status.HTTP_400_BAD_REQUEST)
    if not ids_decoded:
        return Response(status.HTTP_400_BAD_REQUEST)
    id_encoded = base64.b64decode(ids_decoded.encode("ascii")).decode('ascii')
    ids_tuple = tuple(map(int, id_encoded.split(',')))
    Cart.objects.filter(id__in=ids_tuple).update(statusId=2)
    return Response(status.HTTP_200_OK)


def payment_item_gen(title, price, count):
    return {
        "name": title,
        "unit_amount": {
            "currency_code": "USD",
            "value": price
        },
        "quantity": count
    }


def payment_obj_gen(items, id, amount):
    return {
        "purchase_units": [
            {
                "reference_id": id,
                "description": "Some description",
                "custom_id": id,
                "amount": {
                    "currency_code": 'USD',
                    "value": amount,
                    "breakdown": {
                        "item_total": {
                            "currency_code": "USD",
                            "value": amount
                        }
                    }
                },
                "items": items
            }
        ],
    }


@api_view(['POST'])
def make_payment(request):
    # print(request.data)
    # ids_tuple = tuple(map(int, request.data['ids']))
    ids_tuple = (1, 3)
    concerts = (Cart.objects.filter(id__in=ids_tuple)
                .select_related('concertId', 'promocodeId')
                .values('concertId__title', 'concertId__price', 'count', 'promocodeId__discount')
                .annotate(title=F('concertId__title'), price=F('concertId__price'),
                          discount=F('promocodeId__discount')))

    items = []
    amount = 0
    for key in concerts:
        discount = 1
        if key['discount']:
            discount = (1 - key['discount'] / 100)
        price = key['count'] * key['price'] * discount
        amount += price
        items.append(payment_item_gen(key['title'], price, key['count']))

    payment_obj = payment_obj_gen(items, str(uuid.uuid4()), amount)

    return Response(json.dumps(payment_obj), status.HTTP_200_OK)


@api_view(['POST'])
def make_payment2(request):
    if not len(request.data['ids']):
        return Response(status.HTTP_400_BAD_REQUEST)

    ids = tuple(map(int, request.data['ids']))
    concerts = (Cart.objects.filter(id__in=ids)
                .select_related('concertId', 'promocodeId')
                .values('concertId__title', 'concertId__price', 'count', 'promocodeId__discount')
                .annotate(title=F('concertId__title'), price=F('concertId__price'),
                          discount=F('promocodeId__discount')))
    if not len(concerts):
        return Response(status.HTTP_404_NOT_FOUND)
    items = []
    amount = 0
    ids_string = ','.join(str(i) for i in ids)
    ids_string = base64.b64encode(ids_string.encode('ascii')).decode('ascii')
    for key in concerts:
        discount = 1
        if key['discount']:
            discount = (1 - key['discount'] / 100)
        price = key['count'] * key['price'] * discount
        amount += price
        items.append(payment_item_gen(key['title'], price, key['count']))

    payment_obj = payment_obj_gen(items, ids_string, amount)

    return Response(payment_obj, status.HTTP_200_OK)


@api_view(['POST'])
def make_3(request):
    ids_decoded = 'MSwz'
    id_encoded = base64.b64decode(ids_decoded.encode("ascii")).decode('ascii')
    ids_tuple = tuple(map(int, id_encoded.split(',')))
    result = Cart.objects.filter(id__in=ids_tuple).update(statusId=2)
    print(result)
    return Response('1', status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))
def me(request):
    return Response(True, status.HTTP_200_OK)

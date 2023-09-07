import base64
import jwt
from django.core.paginator import Paginator
from django.db.models import F
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from .auth.serializer import MyTokenObtainPairSerializer
from .serializers import *
from .setting import page
from .utils import  email_tickets,payment_item_gen,payment_obj_gen, email_tickets


@api_view(['GET', 'POST'])
@permission_classes((permissions.IsAuthenticated,))
def concert_list(request):
 
    if request.method == 'GET':     
        per_page = request.GET.get("count") or page['itemsPerPage']
        page_number = request.GET.get("page") or page['default']
        keyword = request.GET.get("keyword") or ''
        type = request.GET.get("type") or 0
        ids = request.GET.get("ids") or ''
      
        concerts = (
            Concerts.objects.select_related('typeId', 'placeId', 'singerVoiceId')
            .values('id', 'title', 'date', 'placeId__address', 'typeId_id', 'typeId__title', 'placeId__latitude',
                    'placeId__longitude', 'singerVoiceId__title', 'singerVoiceId_id', 'desc','poster', 'censor', 'price', 'ticket', 'composer', 'concertName'))
      
        if(keyword):
            concerts = concerts.filter(title__iregex=f'{keyword}')
        if int(type) > 0:
            concerts = concerts.filter(typeId_id=type)
        if ids:
            ids_tuple = tuple(map(int, ids.split(',')))
            concerts = concerts.filter(id__in=ids_tuple)
        paginator = Paginator(concerts, per_page)
        paged_concert = paginator.get_page(page_number)     

        serializer = ConcertsSerializerEx(paged_concert, context={'request': request}, many=True)
        output = {'data': serializer.data, 'total': concerts.count()}

        return Response(output, status.HTTP_200_OK)      

    if request.method == 'POST':
       
        serializer = ConcertsExtendedSerializer2(data=request.data)        
        if serializer.is_valid():
            concerts = request.data.copy()           
            new_place = {'address': concerts['address'], 'latitude': concerts['latitude'],
                         'longitude': concerts['longitude']}           
            place_serializer = PlaceSerializer(data=new_place)
            if place_serializer.is_valid():
                place_result = place_serializer.save()
                concerts['placeId'] = place_result.pk
                concerts_serializer = ConcertsSerializer(data=concerts)
                if concerts_serializer.is_valid():
                    result_concerts = concerts_serializer.save()
                    concert = get_concerts(result_concerts.id)                        
                    output = ConcertsSerializerEx(concert, context={'request': request}, many=True)          

                    return Response(output.data, status=status.HTTP_201_CREATED)
                else:

                    return Response(concerts_serializer.errors, status.HTTP_400_BAD_REQUEST)
                
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE', 'GET'])
@permission_classes((permissions.IsAuthenticated,))

def concert(request, pk):
    if not pk:
        return Response('Invalid id', status=status.HTTP_400_BAD_REQUEST)
    try:
        record = Concerts.objects.get(pk=pk)
    except:

        return Response(status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        record.delete()

        return Response(status.HTTP_204_NO_CONTENT)
    
    if request.method == 'PUT':
        serializer = ConcertsSerializer(record, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()         
            concert = get_concerts(pk)             
            output = ConcertsSerializerEx(concert, context={'request': request}, many=True)  

            return Response(output.data, status=status.HTTP_200_OK)  
              
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        concert = get_concerts(pk)         
        serializer = ConcertsSerializerEx(concert, context={'request': request}, many=True)  

        return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))

def concert_type(request):
    data = ConcertType.objects.all()
    serializer = ConcertTypeSerializer(data, context={'request': request}, many=True)

    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated, ))

def singer_voice(request):
    data = SingerVoice.objects.all()
    serializer = SingerVoiceSerializer(data, context={'request': request}, many=True)

    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes((permissions.IsAuthenticated,))

def cart_list(request):

    if request.method == 'GET':
        data = Cart.objects.all()
        serializer = CartSerializer(data, context={'request': request}, many=True)
       
        return Response(serializer.data, status.HTTP_200_OK)
    
    if request.method == 'DELETE':        
        ids = request.query_params.get('ids').split(',')
        if ids:
            try:
                queryset = Cart.objects.filter(id__in=ids)
            except:
                return Response(status.HTTP_400_BAD_REQUEST)
            queryset.delete()
            return Response(queryset.data,status=status.HTTP_204_NO_CONTENT)
        
    if request.method == 'POST':
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status.HTTP_201_CREATED)  
              
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH', 'DELETE', 'GET'])
@permission_classes((permissions.IsAuthenticated,))

def cart_change(request, pk):
    if not pk:
        return Response('Invalid id', status=status.HTTP_400_BAD_REQUEST)
    try:
        record = Cart.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        record.delete()

        return Response(status.HTTP_204_NO_CONTENT)
    
    if request.method == 'PATCH':
        serializer = CartSerializer(record, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response({'id': int(pk), 'data': request.data}, status.HTTP_200_OK)
        
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
@permission_classes((permissions.IsAuthenticated,))
def cart_user(request, uid):
        if not uid:
             return Response('Invalid id', status=status.HTTP_400_BAD_REQUEST)
        try:
            record = (Cart.objects.filter(userId=uid).select_related('concertId', 'promocodeId')
                    .values('id', 'count', 'concertId__title', 'concertId__poster',
                            'concertId__price', 'concertId__ticket', 'promocodeId__discount', 'promocodeId__title'))
        except:
            return Response(status.HTTP_404_NOT_FOUND)
       
        if request.method == 'GET':
            serializer = CartSerializerEx(record, context={'request': request}, many=True)
            
            return Response(serializer.data, status.HTTP_200_OK)
        
        if request.method == 'DELETE':
            try:
                cart = Cart.objects.filter(userId=uid)
                user = User.objects.get(id=uid)
            except:
                return Response(status.HTTP_404_NOT_FOUND)  
            serializer = CartSerializerEx(record, context={'request': request}, many=True)  
            email_tickets(serializer.data, user.email)
            cart.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)


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
@permission_classes((permissions.IsAuthenticated,))
def promocode_find(request):

    promocode = request.data
    if not promocode:

        return Response('', status.HTTP_400_BAD_REQUEST)
    result = Promocode.objects.filter(title=promocode['promocode']).values()

    if not (len(result)):
        return Response(0, status.HTTP_200_OK)
    result = result[0]
    id = result['id']
    title = result['title']
    discount = result['discount']
    cart = Cart.objects.filter(id=promocode['id']).update(promocodeId=id)
    
    if cart:
        output = {'cartId': promocode['id'], 'title': title, 'discount': discount}

        return Response(output, status.HTTP_200_OK)
    
    return Response(status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@permission_classes((permissions.IsAuthenticated, permissions.IsAdminUser,))

def promocode_change(request, pk):
    if not pk:
        return Response('Invalid id', status=status.HTTP_400_BAD_REQUEST)
    try:
        record = Promocode.objects.get(pk=pk)
    except:
        return Response(status.HTTP_404_NOT_FOUND)
    
    if request.method == 'DELETE':
        record.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    if request.method == 'PUT':
        serializer = PromocodeSerializer(record, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status.HTTP_200_OK)
        
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def paypal(request):

    if not request.data:
        return Response(status.HTTP_400_BAD_REQUEST)
    
    ids_decoded = request.data['resource']['purchase_units'][0]['reference_id']
   
    if not ids_decoded:

        return Response(status.HTTP_400_BAD_REQUEST)
    id_encoded = base64.b64decode(ids_decoded.encode("ascii")).decode('ascii')
    ids_tuple = tuple(map(int, id_encoded.split(',')))
    Cart.objects.filter(id__in=ids_tuple).update(statusId=2)

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))

def make_payment(request):
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
        price = round(key['price'] * discount*100,2) / 100
        amount += price * key['count']
        items.append(payment_item_gen(key['title'], price, key['count']))

    payment_obj = payment_obj_gen(items, ids_string, amount)

    return Response(payment_obj, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))

def me(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return Response({'code': 0}, status.HTTP_200_OK)
    token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    token = AccessToken(token)
    user_id = token.payload['user_id']
    user = User.objects.filter(id=user_id)
    if not user:
        return Response({'code': 0}, status.HTTP_200_OK)
    serializer = UserSerializerMe(user, context={'request': request}, many=True)
   
    return Response({'code': 1, 'data': serializer.data[0]}, status.HTTP_200_OK)
 


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))

def social_login(request):

    if not request.data['jwt']:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    token = request.data['jwt']
    decoded = jwt.decode(token, algorithms=["RS256"], options={"verify_signature": False})

    if not decoded:
        return Response(status.HTTP_400_BAD_REQUEST)
    
    email = decoded['email']
    first_name = decoded['given_name']
    last_name = decoded['family_name']
    user = User.objects.filter(username=email).first()

    if not user:
        user = User(username=email, first_name=first_name, last_name=last_name, email=email)
        user.save()
    user_token = MyTokenObtainPairSerializer.get_token(user)
    data = {'refresh': str(user_token), 'access': str(user_token.access_token)} 

    return Response(data, status.HTTP_200_OK)

def get_concerts(id):
    concert = Concerts.objects.filter(id=id).select_related('typeId', 'placeId', 'singerVoiceId').values('id', 'title', 'date', 'placeId__address', 'typeId_id', 'typeId__title', 'placeId__latitude','placeId__longitude', 'singerVoiceId__title', 'singerVoiceId_id', 'poster', 'desc', 'price','ticket', 'composer', 'concertName')
    return concert


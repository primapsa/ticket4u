import base64
import jwt
from django.core.paginator import Paginator
from django.db.models import F
from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from .auth.serializer import MyTokenObtainPairSerializer
from .serializers import *
from rest_framework_simplejwt.backends import TokenBackend
from .utils import email_tickets, payment_item_gen, payment_obj_gen, email_tickets
from rest_framework.views import APIView
from ticket4uApp import settings


class ConcertList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        concerts = self.get_object()
        page = self._get_page_param(request)
        concerts = self._filter(concerts, **self._get_filters_param(request))
        paged = self._paginate(concerts, page['per_page'], page['page_number'])
        serializer = ConcertsTypePlaceSingerSerializer(paged, many=True)

        return Response(self._make_output(serializer), status.HTTP_200_OK)

    def post(self, request):
        serializer = ConcertsAddresSerializer(data=request.data)
        if serializer.is_valid():
            concerts = request.data.copy()
            new_place = self._make_place(concerts)
            place_serializer = PlaceSerializer(data=new_place)
            if place_serializer.is_valid():
                place_result = place_serializer.save()
                concerts['placeId'] = place_result.pk
                concerts_serializer = ConcertsSerializer(data=concerts)
                if concerts_serializer.is_valid():
                    result_concerts = concerts_serializer.save()
                    output = ConcertsTypePlaceSingerSerializer(result_concerts)
                    return Response(output.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(concerts_serializer.errors, status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def _paginate(self, obj, per_page, page):
        paginator = Paginator(obj, per_page)
        return paginator.get_page(page)

    def get_object(self):
        try:
            return Concerts.objects.select_related('typeId', 'placeId', 'singerVoiceId')
        except Concerts.DoesNotExist:
            return None

    def _filter(self, obj, **kwargs):

        for key in kwargs:
            if key == 'keyword':
                obj = obj.filter(title__iregex=f'{kwargs[key]}')
            if key == 'type':
                return obj.filter(typeId_id=kwargs[key])
            if key == 'ids':
                ids_tuple = tuple(map(int, kwargs[key].split(',')))
                obj = obj.filter(id__in=ids_tuple)

        return obj

    def _get_filters_param(self, request):

        names = ['keyword', 'type', 'ids']
        filters = {}
        for name in names:
            if name in request.GET:
                filters[name] = request.GET.get(name)

        return filters

    def _get_page_param(self, request):

        per_page = request.GET.get('count', settings.ITEMS_PER_PAGE)
        page_number = request.GET.get('page', settings.DEFAULT_PAGE)

        return {'per_page': per_page, 'page_number': page_number}

    def _make_place(self, obj):

        address = obj.get('address', '')
        latitude = obj.get('latitude', '')
        longitude = obj.get('longitude', '')

        return {'address': address, 'latitude': latitude, 'longitude': longitude}

    def _make_output(self, obj):

        return {'data': obj.data, 'total': len(obj.data)}


class ConcertDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, relatived=False):
        try:
            if relatived:
                return Concerts.objects.select_related('typeId', 'placeId', 'singerVoiceId').get(id=pk)
            else:
                return Concerts.objects.get(id=pk)
        except Concerts.DoesNotExist:
            return None

    def get(self, pk):
        concert = self.get_object(pk, True)
        serializer = ConcertsTypePlaceSingerSerializer(concert)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        concert = self.get_object(pk)
        serializer = ConcertsSerializer(concert, data=request.data)
        if serializer.is_valid():
            serializer.save()
            concert = self.get_object(pk)
            serializer = ConcertsTypePlaceSingerSerializer(concert)
            return Response([serializer.data], status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, _, pk):
        concert = self.get_object(pk)
        concert.delete()
        return Response('', status=status.HTTP_204_NO_CONTENT)


class ConcertTypeList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConcertTypeSerializer
    queryset = ConcertType.objects.all()


class SingerVoiceList(generics.ListAPIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SingerVoiceSerializer
    queryset = SingerVoice.objects.all()


class CartList(generics.ListCreateAPIView, generics.DestroyAPIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def delete(self, request):
        ids = request.query_params.get('ids')
        if not ids:
            return Response('', status=status.HTTP_400_BAD_REQUEST)
        cart = self._get_cart(ids)

        if not cart:
            return Response('', status=status.HTTP_404_NOT_FOUND)
        cart.delete()
        return Response(cart.data, status=status.HTTP_204_NO_CONTENT)

    def _get_cart(self, ids):

        ids = ids.split(',')
        try:
            return self.get_queryset.filter(id__in=ids)
        except Cart.DoesNotExist:
            return None


class CartDetail(generics.RetrieveDestroyAPIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def patch(self, request, pk):
        serializer = self.get_serializer_class(
            self._get_record(pk), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response({'id': int(pk), 'data': request.data}, status.HTTP_200_OK)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def _get_record(self, pk):
        return self.get_queryset.get(pk=pk)


class CartUserDetail(APIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartUserSerializer

    def delete(self, _, uid):

        cart = self._get_cart(uid)
        user = self._get_user(uid)
        if not (cart or user):
            return Response('', status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(cart,  many=True)
        email_tickets(serializer.data, user.email)
        cart.delete()

        return Response('', status=status.HTTP_204_NO_CONTENT)

    def get(self, _, uid):
        cart_records = self._get_cart(uid)
        if not cart_records:
            return Response('', status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(cart_records, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def _get_cart(self, uid):

        try:
            return Cart.objects.filter(userId=uid).select_related('concertId', 'promocodeId')
        except Cart.DoesNotExist:
            return None

    def _get_user(self, uid):

        try:
            return User.objects.get(id=uid)
        except User.DoesNotExist:
            return None

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)


class PromocodeCardDetail(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        promocode = request.data.get('promocode')
        cart_id = request.data.get('id')
        if not (promocode or cart_id):
            return Response('', status=status.HTTP_400_BAD_REQUEST)

        try:
            promocode_obj = Promocode.objects.get(title=promocode)
        except Promocode.DoesNotExist:
            return Response(0, status=status.HTTP_200_OK)

        cart = Cart.objects.filter(id=cart_id).update(
            promocodeId=promocode_obj.id)

        if cart:
            return Response(self._make_output(cart_id, promocode_obj), status=status.HTTP_200_OK)
        return Response('', status=status.HTTP_400_BAD_REQUEST)

    def _make_output(self, cart_id, obj):
        return {'cartId': cart_id, 'title': obj.title, 'discount': obj.discount}


class PromocodeList(generics.ListCreateAPIView):

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = PromocodeSerializer
    queryset = Promocode.objects.all()

    def get(self, request):
        per_page = request.GET.get('count', settings.ITEMS_PER_PAGE)
        page_number = request.GET.get('page', settings.DEFAULT_PAGE)
        paged = self._paginate(per_page, page_number)
        serializer = self.get_serializer(paged, many=True)
        return Response(self._make_output(serializer), status.HTTP_200_OK)

    def _paginate(self, per_page, page):
        paginator = Paginator(self.get_queryset(), per_page)
        return paginator.get_page(page)

    def _make_output(self, serialized):
        return {'data': serialized.data, 'total': len(serialized.data)}


class PromocodeDetail(generics.DestroyAPIView, generics.UpdateAPIView):

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = PromocodeSerializer
    queryset = Promocode.objects.all()


class Paypal(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ids_decoded = request.data['resource']['purchase_units'][0]['reference_id'] or None
        if not ids_decoded:
            return Response('', status.HTTP_400_BAD_REQUEST)
        Cart.objects.filter(id__in=self._extract_ids(
            ids_decoded)).update(statusId=2)
        return Response('', status=status.HTTP_200_OK)

    def _extract_ids(self, decoded):
        id_encoded = base64.b64decode(decoded.encode("ascii")).decode('ascii')
        return tuple(map(int, id_encoded.split(',')))


class Payment(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ids = self._get_ids(request)
        concerts = self.get_object(ids)
        if not concerts:
            return Response('', status.HTTP_404_NOT_FOUND)
        payment = self._make_payment(concerts, ids)
        if not payment:
            return Response('', status.HTTP_400_BAD_REQUEST)

        return Response(payment, status.HTTP_200_OK)

    def get_object(self, ids):
        try:
            return Cart.objects.filter(id__in=ids).select_related('concertId', 'promocodeId').values('concertId__title', 'concertId__price', 'count', 'promocodeId__discount').annotate(title=F('concertId__title'), price=F('concertId__price'), discount=F('promocodeId__discount'))
        except Cart.DoesNotExist:
            return None

    def _get_ids(self, request):
        ids = request.data.get('ids', None)
        if ids:
            return tuple(map(int, ids))
        return None

    def _ids_encode(self, ids):
        ids_string = ','.join(str(i) for i in ids)
        ids_encoded = base64.b64encode(
            ids_string.encode('ascii')).decode('ascii')
        return ids_encoded

    def _make_payment(self, obj, ids):
        try:
            items = []
            amount = 0
            for key in obj:
                discount = 1
                if key['discount']:
                    discount = (1 - key['discount'] / 100)
                price = round(key['price'] * discount*100, 2) / 100
                amount += price * key['count']
                items.append(self._make_payment_item(
                    key['title'], price, key['count']))
            ids = self._ids_encode(ids)
            return self._make_payment_unit(items, ids, amount)
        except:
            return None

    def _make_payment_item(self, title, price, count, currency='USD'):
        return {
            "name": title,
            "unit_amount": {
                "currency_code": currency,
                "value": price
            },
            "quantity": count
        }

    def _make_payment_unit(items, id, amount, currency='USD'):
        return {
            "purchase_units": [
                {
                    "reference_id": id,
                    "description": "T4u market",
                    "custom_id": id,
                    "amount": {
                        "currency_code": currency,
                        "value": amount,
                        "breakdown": {
                            "item_total": {
                                "currency_code": currency,
                                "value": amount
                            }
                        }
                    },
                    "items": items
                }
            ],
        }


class Me(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializerMe
    queryset = User.objects.all()

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', ' ')
        if not token:
            return Response('', status=status.HTTP_400_BAD_REQUEST)
        token = token.split(' ')[1]
        token = AccessToken(token)
        user_id = token.payload.get('user_id', None)
        if not user_id:
            return Response('', status=status.HTTP_400_BAD_REQUEST)
        user = self.get_user(user_id)
        if not user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(user, context={'request': request})

        return Response(serializer.data, status.HTTP_200_OK)

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None


class SocialLogin(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('jwt', None)
        if not token:
            return Response('', status=status.HTTP_400_BAD_REQUEST)

        decoded = self.decode_token(token)
        if not decoded:
            return Response('', status=status.HTTP_400_BAD_REQUEST)

        email = decoded.get('email')
        first_name = decoded.get('given_name')
        last_name = decoded.get('family_name')

        user = self.get_or_create_user(email, first_name, last_name)
        user_token = self.generate_user_token(user)

        return Response(self._make_output(user_token), status=status.HTTP_200_OK)

    def decode_token(self, token):
        try:
            return jwt.decode(token, algorithms=["RS256"], options={"verify_signature": False})
        except jwt.DecodeError:
            return None

    def _make_output(self, token):
        return {'refresh': str(token), 'access': str(token.access_token)}

    def get_or_create_user(self, email, first_name, last_name):
        user = User.objects.filter(username=email).first()

        if not user:
            user = User(username=email, first_name=first_name,
                        last_name=last_name, email=email)
            user.save()

        return user

    def generate_user_token(self, user):
        return MyTokenObtainPairSerializer.get_token(user)

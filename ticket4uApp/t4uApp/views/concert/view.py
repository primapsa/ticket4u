from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from t4uApp.serializers import *
from rest_framework.views import APIView
from ticket4uApp import settings
from t4uApp.models import (
    Concert,
    ConcertType,
    SingerVoice,
    Place,
    Classic,
    Openair,
    Party,
)
from django.db import transaction
from django.db.models import Q
import json
from rest_framework.exceptions import ErrorDetail


class BaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializers = [ConcertClassicSerializer, ConcertPartySerializer, ConcertOpenairSerializer]
    models = [Classic, Party, Openair]

    def convert_to_dict(self, listed_obj):
        if listed_obj:
            dict_obj = {}
            for name in listed_obj:
                if type(listed_obj[name]) is str:
                    try:
                        dict_obj[name] = json.loads(listed_obj[name])
                    except:
                        dict_obj[name] = listed_obj[name]
                else:
                    dict_obj[name] = listed_obj[name]
            return dict_obj
        return None

    def get_errors(self, error_dict):
        error_list = []
        for field, errors in error_dict.items():
            if isinstance(errors, list):
                for error in errors:
                    if isinstance(error, ErrorDetail):
                        error_list.append({field: f"{error}"})
            elif isinstance(errors, dict):
                for key, error in errors.items():
                    if isinstance(error, list):
                        for detail in error:
                            if isinstance(detail, ErrorDetail):
                                error_list.append({field: f"{detail}"})
            else:
                error_list.append({field: "Неизвестная ошибка"})

        return error_list

    def get_serializer_by_type_id(self, type_id):
        if type_id > 0:
            return self.serializers[int(type_id) - 1]
        return None


class ConcertList(BaseView):

    def get(self, request):
        concerts = self.get_object()
        page = self._get_page_param(request)
        concerts = self._filter(concerts, **self._get_filters_param(request))
        total = concerts.count()
        paged = self._paginate(concerts, page["per_page"], page["page_number"])
        serializer = ConcertsWithRelativesSerializer(paged, many=True)

        return Response(self._make_output(serializer, total), status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request):
        concert_data = self.convert_to_dict(request.data)
        concert_type_id = concert_data.get('type', None)
        processed_request = self._process_request(request, concert_data)
        if processed_request:
            return processed_request
        if not concert_type_id:
            return Response({'general': 'Ошибка данных!'}, status.HTTP_400_BAD_REQUEST)
        concert = self._process_concert(concert_type_id, concert_data)
        if concert:
            return Response(concert, status.HTTP_201_CREATED)

        return Response(self.get_errors(concert_result.errors), status.HTTP_400_BAD_REQUEST)

    def _process_request(self, request, concert_data):
        concert_data['poster'] = request.FILES.get('poster', None)
        concert_data_serializer = ConcertsSerializer(data=concert_data)
        place_data = concert_data.get('place', {})
        place_serializer = PlaceSerializer(data=place_data)
        if not concert_data_serializer.is_valid():
            return Response(self._get_errors(concert_data_serializer.errors), status.HTTP_400_BAD_REQUEST)
        if not self._is_title_unique(concert_data):
            return Response({"title": "Заголовок уже используется"}, status.HTTP_400_BAD_REQUEST)
        if not place_serializer.is_valid():
            return Response(self._get_errors(place_serializer.errors), status.HTTP_400_BAD_REQUEST)
        return None

    def _process_concert(self, concert_type_id, concert_data):
        concert_serializer = self.get_serializer_by_type_id(concert_type_id)
        concert_result = concert_serializer(data=concert_data)
        response = None
        if concert_result.is_valid():
            concert = concert_result.save()
            output = concert_serializer(concert)
            response = output.data
        return response

    def _paginate(self, obj, per_page, page):
        paginator = Paginator(obj, per_page)
        return paginator.get_page(page)

    def _is_title_unique(self, concerts):
        title = concerts.get("title")
        date = concerts.get("date")
        address = concerts.get("address")
        is_unique = not Concert.objects.filter(
            Q(title=title) & Q(date=date) & Q(place__address=address)
        ).exists()

        return is_unique

    def get_object(self):
        try:
            return Concert.objects.all().select_related('party', 'openair', 'classic')
        except Concert.DoesNotExist:
            return None

    def _filter(self, obj, **kwargs):
        for key in kwargs:
            if key == "keyword":
                obj = obj.filter(title__iregex=f"{kwargs[key]}")
            if key == "type":
                return obj.filter(type_id=kwargs[key])
            if key == "ids":
                ids_tuple = tuple(map(int, kwargs[key].split(",")))
                obj = obj.filter(id__in=ids_tuple)
        return obj

    def _get_filters_param(self, request):
        names = ["keyword", "type", "ids"]
        filters = {}
        for name in names:
            if name in request.GET:
                filters[name] = request.GET.get(name)
        return filters

    def _get_page_param(self, request):
        per_page = request.GET.get("count", settings.ITEMS_PER_PAGE)
        page_number = request.GET.get("page", settings.DEFAULT_PAGE)

        return {"per_page": per_page, "page_number": page_number}

    def _make_output(self, obj, total):
        return {"data": obj.data, "total": total}


class ConcertDetail(BaseView):

    def get_object(self, pk):
        try:
            return Concert.objects.all().select_related('party', 'openair', 'classic').get(id=pk)
        except Concert.DoesNotExist:
            return None

    def _get_model_by_type_id(self, type_id, pk):
        model = self.models[int(type_id) - 1]
        try:
            return model.objects.all().get(id=pk)
        except model.DoesNotExist:
            return None

    def get(self, _, pk):
        concert = self.get_object(pk)
        serializer = ConcertsWithRelativesSerializer(concert)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        update_data = self.convert_to_dict(request.data)
        type_id = update_data.get('type')
        current_concert = self._get_model_by_type_id(type_id, pk)
        concerts_serializer = self.get_serializer_by_type_id(type_id)
        concerts = concerts_serializer(current_concert, data=update_data)
        if concerts.is_valid():
            saved = concerts.save()
            saved.refresh_from_db()
            saved.place.refresh_from_db()
            output = ConcertsWithRelativesSerializer(saved)
            return Response([output.data], status=status.HTTP_200_OK)
        return Response(self.get_errors(concerts.errors), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, _, pk):
        concert = self.get_object(pk)
        concert.delete()
        return Response("", status=status.HTTP_204_NO_CONTENT)


class ConcertTypeList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConcertTypeSerializer
    queryset = ConcertType.objects.all()


class SingerVoiceList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SingerVoiceSerializer
    queryset = SingerVoice.objects.all()

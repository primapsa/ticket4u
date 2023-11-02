from django.core.paginator import Paginator
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from t4uApp.serializers import *
from rest_framework.views import APIView
from ticket4uApp import settings
from t4uApp.models import (
    Concerts,
    ConcertType,
    SingerVoice,
    ConcertExtra,
    Place,
    ConcertClassic,
    ConcertOpenair,
    ConcertParty,
    ConcertExtra,
)
from django.db import transaction
from django.db.models import Q


class ConcertList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        concerts = self.get_object()
        page = self._get_page_param(request)
        concerts = self._filter(concerts, **self._get_filters_param(request))
        total = concerts.count()
        paged = self._paginate(concerts, page["per_page"], page["page_number"])
        serializer = ConcertsTypePlaceSingerSerializer(paged, many=True)

        return Response(self._make_output(serializer, total), status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request):
        serializer = ConcertsAddresSerializer(data=request.data)

        if serializer.is_valid():
            concerts = request.data.copy()
            if not self._is_title_unique(concerts):
                return Response(
                    {"title": "Заголовок уже используется"}, status.HTTP_400_BAD_REQUEST
                )
            new_place = self._make_place(concerts)
            place_serializer = PlaceSerializer(data=new_place)
            if place_serializer.is_valid():
                place_result = place_serializer.save()
                concerts["placeId"] = place_result.pk
                extra_id = self._expand_concerts(concerts)
                if not extra_id:
                    return Response("", status.HTTP_400_BAD_REQUEST)
                concerts["extra"] = extra_id
                concerts_serializer = ConcertsSerializer(data=concerts)
                if concerts_serializer.is_valid():
                    result_concerts = concerts_serializer.save()
                    output = ConcertsTypePlaceSingerSerializer(result_concerts)
                    return Response(output.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        concerts_serializer.errors, status.HTTP_400_BAD_REQUEST
                    )
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def _paginate(self, obj, per_page, page):
        paginator = Paginator(obj, per_page)
        return paginator.get_page(page)

    def _is_title_unique(self, concerts):
        title = concerts.get("title")
        date = concerts.get("date")
        address = concerts.get("address")
        is_unique = not Concerts.objects.filter(
            Q(title=title) & Q(date=date) & Q(placeId__address=address)
        ).exists()

        return is_unique

    def _expand_concerts(self, concerts):
        extra_seralizers = [
            [ConcertClassicSerializer, "classic"],
            [ConcertPartySerializer, "party"],
            [ConcertOpenairSerializer, "openair"],
        ]
        type_id = int(concerts["typeId"]) - 1
        concert_extra_serializers = extra_seralizers[type_id][0]
        concert_extra_field = extra_seralizers[type_id][1]
        concert_extra_info = concert_extra_serializers(data=concerts)
        if concert_extra_info.is_valid():
            res_concert_extra_info = concert_extra_info.save()
            fields = {concert_extra_field: res_concert_extra_info}
            concert_extra = ConcertExtra.objects.create(**fields)

            return concert_extra.pk
        return None

    def get_object(self):
        try:
            return Concerts.objects.select_related("typeId", "placeId")
        except Concerts.DoesNotExist:
            return None

    def _filter(self, obj, **kwargs):
        for key in kwargs:
            if key == "keyword":
                obj = obj.filter(title__iregex=f"{kwargs[key]}")
            if key == "type":
                return obj.filter(typeId_id=kwargs[key])
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

    def _make_place(self, obj):
        address = obj.get("address", "")
        latitude = obj.get("latitude", "")
        longitude = obj.get("longitude", "")

        return {"address": address, "latitude": latitude, "longitude": longitude}

    def _make_output(self, obj, total):
        return {"data": obj.data, "total": total}


class ConcertDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, relatived=False):
        try:
            if relatived:
                return Concerts.objects.select_related("typeId", "placeId").get(id=pk)
            else:
                return Concerts.objects.get(id=pk)
        except Concerts.DoesNotExist:
            return None

    def get(self, _, pk):
        concert = self.get_object(pk, True)
        serializer = ConcertsTypePlaceSingerSerializer(concert)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        concert = self.get_object(pk)

        serializer = ConcertsUpdateSerializer(concert, data=request.data)
        if serializer.is_valid():
            place = self._make_place(request.data)
            self._update_place(place, concert.placeId_id)
            result = self._update_extra(concert, request.data)
            if result:
                return result
            serializer.save()
            concert = self.get_object(pk)
            serializer = ConcertsTypePlaceSingerSerializer(concert)
            return Response([serializer.data], status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, _, pk):
        concert = self.get_object(pk)
        concert.delete()
        return Response("", status=status.HTTP_204_NO_CONTENT)

    def _update_extra(self, current_data, extra_data):
        extra_type_id = int(extra_data.get("typeId"))
        concert_type = extra_type_id - 1
        extra = [
            {
                "singerVoiceId": extra_data.get("singerVoiceId", ""),
                "concertName": extra_data.get("concertName", ""),
                "composer": extra_data.get("composer", ""),
            },
            {"censor": extra_data.get("censor", "")},
            {
                "wayHint": extra_data.get("wayHint", ""),
                "headliner": extra_data.get("headliner", ""),
            },
        ]
        extra_serializers = [
            [ConcertClassicSerializer, ConcertClassic, "classic"],
            [ConcertPartySerializer, ConcertParty, "party"],
            [ConcertOpenairSerializer, ConcertOpenair, "openair"],
        ]
        serializer = extra_serializers[concert_type][0]
        model = extra_serializers[concert_type][1]
        field = extra_serializers[concert_type][2]
        current_extra_id = getattr(current_data.extra, field + "_id")
        target = self._get_object_by_id(model, current_extra_id)

        if current_data.typeId_id != extra_type_id:
            model_field = self._get_field_name_by_id(current_data.extra_id)
            current_model = self._get_model_by_field(model_field, extra_serializers)
            current_target_id = getattr(current_data.extra, model_field + "_id")
            current_target = self._get_object_by_id(current_model, current_target_id)
            current_target.delete()
            create_model = serializer(data=extra[concert_type])
            if create_model.is_valid():
                create_model_result = create_model.save()
                concerts_extra = self._get_object_by_id(
                    ConcertExtra, current_data.extra_id
                )
                update_concerts_extra = ConcertExtraSerializer(
                    concerts_extra, data={field: create_model_result.pk}
                )
                if update_concerts_extra.is_valid():
                    update_concerts_extra.save()
        else:
            update_model = serializer(target, data=extra[concert_type])
            if update_model.is_valid():
                update_model.save()
            else:     
                return Response(self._get_error(update_model.errors), status.HTTP_400_BAD_REQUEST)
        return None
    
    def _get_error(self, error_dict):
        errors = {}
        for err in error_dict:
            errors[err] = error_dict[err][0]
        return errors

    def _get_field_name_by_id(self, id):        
        extra_concert = ConcertExtra.objects.get(id=id)
        fields = ["party", "openair", "classic"]
        for field in fields:
            if getattr(extra_concert, field) is not None:
                return field
        return None

    def _get_model_by_field(self, field, extra):
        for item in extra:
            if item[2] == field:
                return item[1]
        return None

    def _update_place(self, place_data, pk):
        place = self._get_object_by_id(Place, pk)
        if place:
            place_serializer = PlaceSerializer(place, data=place_data)
            if place_serializer.is_valid():
                place_serializer.save()

    def _make_place(self, obj):
        address = obj.get("address", "")
        latitude = obj.get("latitude", "")
        longitude = obj.get("longitude", "")

        return {"address": address, "latitude": latitude, "longitude": longitude}

    def _get_object_by_id(self, obj, pk):
        try:
            return obj.objects.get(id=pk)
        except obj.DoesNotExist:
            return None


class ConcertTypeList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConcertTypeSerializer
    queryset = ConcertType.objects.all()


class SingerVoiceList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SingerVoiceSerializer
    queryset = SingerVoice.objects.all()

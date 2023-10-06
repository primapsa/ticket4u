
from django.core.paginator import Paginator
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from t4uApp.serializers import *
from rest_framework.views import APIView
from ticket4uApp import settings
from t4uApp.models.models import Concerts, ConcertType, SingerVoice


class ConcertList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        concerts = self.get_object()
        page = self._get_page_param(request)
        concerts = self._filter(concerts, **self._get_filters_param(request))
        paged = self._paginate(concerts, page["per_page"], page["page_number"])
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
                concerts["placeId"] = place_result.pk
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

    def get_object(self):
        try:
            return Concerts.objects.select_related("typeId", "placeId", "singerVoiceId")
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

    def _make_output(self, obj):
        return {"data": obj.data, "total": len(obj.data)}


class ConcertDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, relatived=False):
        try:
            if relatived:
                return Concerts.objects.select_related(
                    "typeId", "placeId", "singerVoiceId"
                ).get(id=pk)
            else:
                return Concerts.objects.get(id=pk)
        except Concerts.DoesNotExist:
            return None

    def get(self, _ , pk):
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
        return Response("", status=status.HTTP_204_NO_CONTENT)


class ConcertTypeList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConcertTypeSerializer
    queryset = ConcertType.objects.all()

class SingerVoiceList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SingerVoiceSerializer
    queryset = SingerVoice.objects.all()
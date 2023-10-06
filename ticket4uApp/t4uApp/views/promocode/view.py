from django.core.paginator import Paginator
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from t4uApp.serializers import *
from rest_framework.views import APIView
from ticket4uApp import settings
from t4uApp.models.models import *

class PromocodeCardDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        promocode = request.data.get("promocode")
        cart_id = request.data.get("id")
        if not (promocode or cart_id):
            return Response("", status=status.HTTP_400_BAD_REQUEST)
        try:
            promocode_obj = Promocode.objects.get(title=promocode)
        except Promocode.DoesNotExist:
            return Response(0, status=status.HTTP_200_OK)
        cart = Cart.objects.filter(id=cart_id).update(promocodeId=promocode_obj.id)

        if cart:
            return Response(
                self._make_output(cart_id, promocode_obj), status=status.HTTP_200_OK
            )
        return Response("", status=status.HTTP_400_BAD_REQUEST)

    def _make_output(self, cart_id, obj):
        return {"cartId": cart_id, "title": obj.title, "discount": obj.discount}


class PromocodeList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = PromocodeSerializer
    queryset = Promocode.objects.all()

    def get(self, request):
        per_page = request.GET.get("count", settings.ITEMS_PER_PAGE)
        page_number = request.GET.get("page", settings.DEFAULT_PAGE)
        total = self.get_queryset().count()
        paged = self._paginate(per_page, page_number)
        serializer = self.get_serializer(paged, many=True)
        return Response(self._make_output(serializer,total), status.HTTP_200_OK)

    def _paginate(self, per_page, page):
        paginator = Paginator(self.get_queryset(), per_page)
        return paginator.get_page(page)

    def _make_output(self, serialized, total):
        return {"data": serialized.data, "total": total}


class PromocodeDetail(generics.DestroyAPIView, generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = PromocodeSerializer
    queryset = Promocode.objects.all()
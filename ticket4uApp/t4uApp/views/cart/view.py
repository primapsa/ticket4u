from rest_framework import status, permissions, generics
from rest_framework.response import Response
from t4uApp.serializers import *
from t4uApp.utils import email_tickets
from rest_framework.views import APIView
from django.contrib.auth.models import User
from t4uApp.models.models import *


class CartList(generics.ListCreateAPIView, generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def delete(self, request):
        ids = request.query_params.get("ids")
        if not ids:
            return Response("", status=status.HTTP_400_BAD_REQUEST)
        cart = self._get_cart(ids)

        if not cart:
            return Response("", status=status.HTTP_404_NOT_FOUND)
        cart.delete()
        return Response(cart.data, status=status.HTTP_204_NO_CONTENT)

    def _get_cart(self, ids):
        ids = ids.split(",")
        try:
            return self.get_queryset.filter(id__in=ids)
        except Cart.DoesNotExist:
            return None


class CartDetail(generics.RetrieveDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def patch(self, request, pk):
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()

            return Response({"id": int(pk), "data": request.data}, status.HTTP_200_OK)
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
            return Response("", status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(cart, many=True)
        email_tickets(serializer.data, user.email)
        cart.delete()

        return Response("", status=status.HTTP_204_NO_CONTENT)

    def get(self, _, uid):
        cart_records = self._get_cart(uid)
        serializer = self.get_serializer(cart_records, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def _get_cart(self, uid):
        try:
            return Cart.objects.filter(userId=uid).select_related(
                "concertId", "promocodeId"
            )
        except Cart.DoesNotExist:
            return None

    def _get_user(self, uid):
        try:
            return User.objects.get(id=uid)
        except User.DoesNotExist:
            return None

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

import base64
from rest_framework.response import Response
from t4uApp.serializers import *
from rest_framework.views import APIView
from rest_framework import status, permissions
from t4uApp.models import *

class Paypal(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ids_decoded = (
            request.data["resource"]["purchase_units"][0]["reference_id"] or None
        )
        if not ids_decoded:
            return Response("", status.HTTP_400_BAD_REQUEST)
        Cart.objects.filter(id__in=self._extract_ids(ids_decoded)).update(statusId=2)
        return Response("", status=status.HTTP_200_OK)

    def _extract_ids(self, decoded):
        id_encoded = base64.b64decode(decoded.encode("ascii")).decode("ascii")
        return tuple(map(int, id_encoded.split(",")))


class Payment(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ids = self._get_ids(request)
        concerts = self.get_object(ids)
        serializer = CartPaymentSerializer(concerts, many=True)
        concerts = serializer.data
        if not concerts:
            return Response("", status.HTTP_404_NOT_FOUND)
        payment = self._make_payment(concerts, ids)
        if not payment:
            return Response("", status.HTTP_400_BAD_REQUEST)
        return Response(payment, status.HTTP_200_OK)

    def get_object(self, ids):
        try:
            return Cart.objects.filter(id__in=ids).select_related(
                "concertId", "promocodeId"
            )
        except Cart.DoesNotExist:
            return None

    def _get_ids(self, request):
        ids = request.data.get("ids", None)
        if ids:
            return tuple(map(int, ids))
        return None

    def _ids_encode(self, ids):
        ids_string = ",".join(str(i) for i in ids)
        ids_encoded = base64.b64encode(ids_string.encode("ascii")).decode("ascii")
        return ids_encoded

    def _calculate_discount(self, key):
        if key["discount"]:
            return 1 - key["discount"] / 100
        return 1

    def _calculate_price(self, key, discount):
        return round(key["price"] * discount * 100, 2) / 100

    def _calculate_amount(self, obj):
        amount = 0
        for key in obj:
            discount = self._calculate_discount(key)
            price = self._calculate_price(key, discount)
            amount += price * key["count"]
        return amount

    def _create_items_list(self, obj):
        items = []
        for key in obj:
            discount = self._calculate_discount(key)
            price = self._calculate_price(key, discount)
            items.append(self._make_payment_item(key["title"], price, key["count"]))
        return items

    def _make_payment(self, obj, ids):
        try:
            items = self._create_items_list(obj)
            amount = self._calculate_amount(obj)
            ids = self._ids_encode(ids)
            return self._make_payment_unit(items, ids, amount)
        except:
            return None

    def _make_payment_item(self, title, price, count, currency="USD"):
        return {
            "name": title,
            "unit_amount": {"currency_code": currency, "value": price},
            "quantity": count,
        }

    def _make_payment_unit(self, items, ids, amount, currency="USD"):
        return {
            "purchase_units": [
                {
                    "reference_id": ids,
                    "description": "T4u market",
                    "custom_id": ids,
                    "amount": {
                        "currency_code": currency,
                        "value": amount,
                        "breakdown": {
                            "item_total": {"currency_code": currency, "value": amount}
                        },
                    },
                    "items": items,
                }
            ],
        }

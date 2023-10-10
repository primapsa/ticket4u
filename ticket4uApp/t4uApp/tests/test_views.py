from django.test import TestCase
from t4uApp.models.models import (
    Promocode,
    ConcertType,
    Place,
    Concerts,
    SingerVoice,
    Cart,
    TicketStatus    
)
from django.contrib.auth.models import User
from rest_framework import status
from t4uApp.serializers.user import TokenLoginSerializer
from rest_framework.test import APIClient
from django.utils import timezone
import jwt
import json



class BaseCaseTest(TestCase):
    def setUp(self):
        self.email = "t4u.user@onrender.com"
        self.username = "t4uuser"
        self.password = "12345679"
        self.user = User.objects.create_user(self.username, self.email, self.password)

        self.data = {"username": self.username, "password": self.password}


class TokenizedTestCase(BaseCaseTest):
    def setUp(self):
        super().setUp()
        client = APIClient()
        self.token = str(TokenLoginSerializer.get_token(self.user).access_token)
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        self.client = client


class AuthTest(BaseCaseTest):
    def setUp(self):
        self.url_login = "/api/v1/user/login/"
        self.url_me = "/api/v1/user/me/"
        self.url_register = "/api/v1/user/register/"
        self.client = APIClient()
        return super().setUp()

    def test_correct_jwt_token_login(self):
        response = self.client.post(self.url_login, self.data, format="json")
        token = response.data.get("access")
        decoded = jwt.decode(
            token, algorithms=["RS256"], options={"verify_signature": False}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(decoded["user_id"], 1)
        self.assertEqual(decoded["email"], self.email)
        self.assertEqual(decoded["is_staff"], False)

    def test_me_without_token(self):
        response = self.client.get(self.url_me)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_me_with_correct_token(self):
        response = self.client.post(self.url_login, self.data, format="json")
        token = response.data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

        me_response = self.client.get(self.url_me, format="json")

        self.assertEqual(me_response.status_code, status.HTTP_200_OK)

    def test_with_incorrect_pwd(self):
        data_incorrect = self.data.copy()
        data_incorrect["password"] = "fake"
        response = self.client.post(self.url_login, data_incorrect, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_with_incorrect_usernname(self):
        data_incorrect = self.data.copy()
        data_incorrect["username"] = "fake_usrname"
        response = self.client.post(self.url_login, data_incorrect, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_exist_user(self):
        response = self.client.post(self.url_register, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, "Пользователь уже существует")

    def test_register_new_user(self):
        new_user = {
            "username": "user123456",
            "email": "user123456@mail.com",
            "password": "qwerty1346",
        }
        response = self.client.post(self.url_register, new_user, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SingerVoiceTest(TokenizedTestCase):
    def setUp(self):
        self.singer_voice1 = SingerVoice.objects.create(title="Singer Voice 1")
        self.singer_voice2 = SingerVoice.objects.create(title="Singer Voice 2")
        self.url = "/api/v1/voice/"
        return super().setUp()

    def test_get_singer_voices(self):
        response = self.client.get(self.url, format="json")
        expected_data = [
            {"value": str(self.singer_voice1.id), "label": "Singer Voice 1"},
            {"value": str(self.singer_voice2.id), "label": "Singer Voice 2"},
        ]
        self.assertEqual(json.loads(response.content), expected_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class CartTest(TokenizedTestCase):
    def setUp(self):
        self.concert = Concerts.objects.create(title="concertr")
        self.promocode = Promocode.objects.create(title="promocode", discount=1)
        self.cart = Cart.objects.create(
            userId=1, concertId=self.concert, promocodeId=self.promocode, count=1
        )
        return super().setUp()


class CartListTest(CartTest):
    def setUp(self):
        self.url = "/api/v1/cart/"
        return super().setUp()

    def test_cart_list(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_cart_delete_without_id(self):
        response = self.client.delete(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CartDetailTest(CartTest):
    def setUp(self):
        self.url = "/api/v1/cart/1"

        return super().setUp()

    def test_patch_cart(self):
        update = {"count": 2}
        response = self.client.patch(self.url, update, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("data").get("count"), 2)

    def test_cart_delete(self):
        response = self.client.delete(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, None)

    def test_incorrect_id_delete(self):
        url_incorrect = "/api/v1/cart/100"
        response = self.client.delete(url_incorrect, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_incorrect_id_patch(self):
        url_incorrect = "/api/v1/cart/100"
        response = self.client.delete(url_incorrect, {"count": 25}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CartUserDetailTest(CartTest):
    def setUp(self):
        self.url = "/api/v1/cart/user/1"
        self.ticket_status_1 = TicketStatus.objects.create(title =1)
        self.ticket_status_2 = TicketStatus.objects.create(title =2)
        return super().setUp()

    def test_get_cart_user(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user_cart(self):
        response = self.client.delete(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)


class ConcertTestCase(TokenizedTestCase):
    def setUp(self):
        self.concert_type = ConcertType.objects.create(title="type1")
        self.singer_voice = SingerVoice.objects.create(title="voice1")
        self.place = Place.objects.create(
            address="minsk", latitude="2.55", longitude="5.222"
        )
        self.concert = Concerts.objects.create(
            title="concert",
            desc="Test Description",
            date=timezone.now(),
            price=10.0,
            typeId=self.concert_type,
            singerVoiceId=self.singer_voice,
            placeId=self.place,
        )
        return super().setUp()


class ConcertTest(ConcertTestCase):
    def setUp(self):
        self.url = "/api/v1/concerts/"
        return super().setUp()

    def test_get_concerts(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_concert_by_filter_keyword(self):
        url = self.url + "?keyword=concert"
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(dict(response.data.get("data")[0])["id"], 1)

    def test_get_concert_by_filter_type(self):
        url = self.url + "?type=1"
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(dict(response.data.get("data")[0])["id"], 1)

    def test_get_concert_by_filter_ids(self):
        url = self.url + "?ids=1"
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(dict(response.data.get("data")[0])["id"], 1)

    def test_create_new_concert(self):
        new_concert = {
            "title": "concert1",
            "date": timezone.now(),
            "typeId": self.concert_type.id,
            "singerVoiceId": self.singer_voice.id,
            "concertName": None,
            "composer": None,
            "wayHint": None,
            "headliner": None,
            "censor": None,
            "address": "Minsk",
            "latitude": "4.25555",
            "longitude": "5.5555",
            "price": 100,
            "ticket": 100,
        }
        response = self.client.post(self.url, new_concert, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("id"), 2)


class ConcertDetailTest(ConcertTestCase):
    def setUp(self):
        self.url = "/api/v1/concerts/1"
        return super().setUp()

    def test_update_concert(self):
        data = {
            "title": "Updated Test Concert",
            "desc": "Updated Test Description",
            "date": timezone.now(),
            "price": 20.0,
            "typeId": self.concert_type.pk,
            "singerVoiceId": self.singer_voice.pk,
            "placeId": self.place.pk,
        }
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["title"], data["title"])
        self.assertEqual(response.data[0]["desc"], data["desc"])
        self.assertEqual(response.data[0]["price"], data["price"])

    def test_delte_concert(self):
        response = self.client.delete(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(Concerts.objects.filter(id=1).first())


class ConcertTypeTest(TokenizedTestCase):
    def setUp(self):
        self.url = "/api/v1/type/"
        self.concert_type = ConcertType.objects.create(title="type1")
        return super().setUp()

    def test_get_concert_type_list(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(dict(response.data[0])["label"], "type1")


class PaymenCaseTest(TokenizedTestCase):
    def setUp(self):
        super().setUp()
        self.concert_type = ConcertType.objects.create(title="Test Type")
        self.singer_voice = SingerVoice.objects.create(title="Test Singer Voice")
        self.place = Place.objects.create(
            address="minsk", latitude="0.0", longitude="0.0"
        )
        self.concert = Concerts.objects.create(
            title="Test Concert",
            desc="Test Description",
            date=timezone.now(),
            price=10.0,
            typeId=self.concert_type,
            singerVoiceId=self.singer_voice,
            placeId=self.place,
        )
        self.cart = Cart.objects.create(
            userId=self.user.id, concertId=self.concert, count=1, statusId=1
        )


class PaymentTest(PaymenCaseTest):
    def setUp(self):
        super().setUp()
        self.url = "/api/v1/paypal/create/"

    def test_payment_creation(self):
        data = {"ids": [self.cart.pk]}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("purchase_units", response.data)
        self.assertEqual(len(response.data["purchase_units"]), 1)
        purchase_unit = response.data["purchase_units"][0]
        item = purchase_unit["items"][0]
        self.assertEqual(purchase_unit["amount"]["value"], 10.0)
        self.assertEqual(len(purchase_unit["items"]), 1)
        self.assertEqual(item["name"], "Test Concert")
        self.assertEqual(item["unit_amount"]["value"], 10.0)
        self.assertEqual(item["quantity"], 1)

    def test_payment_with_invaild_id(self):
        data = {"ids": [2]}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PaypalTest(PaymenCaseTest):
    def setUp(self):
        self.url = "/api/v1/paypal/webhook/"
        return super().setUp()

    def test_paypal_webhook_by_id(self):
        data = {"resource": {"purchase_units": [{"reference_id": "MQ=="}]}}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Cart.objects.get(id=1).statusId, 2)

    def test_paypal_webhook_without_id(self):
        data = {"resource": {"purchase_units": [{"reference_id": ""}]}}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokinizedAdminTest(BaseCaseTest):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create(
            username=self.username + "1",
            email=self.email + "1",
            password=self.password,
            is_staff=True,
        )
        client = APIClient()
        self.token = str(TokenLoginSerializer.get_token(self.user).access_token)
        client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        self.client = client


class PromocodeCaseTest(TokinizedAdminTest):
    def setUp(self):
        self.promocode = Promocode.objects.create(
            title="promocode1", date=timezone.now(), discount=5
        )
        return super().setUp()


class PromocodeListTest(PromocodeCaseTest):
    def setUp(self):
        self.url = "/api/v1/promocodes/"
        return super().setUp()

    def test_get_promocodes(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 1)

    def test_create_new_promocode(self):
        data = {"title": "promocode2", "discount": 10}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["id"], 2)


class PromocodeDetailTest(PromocodeCaseTest):
    def setUp(self):
        self.url = "/api/v1/promocodes/1"
        return super().setUp()

    def test_update_promocode_by_if(self):
        data = {"title": "newpromocode", "discount": 20}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.promocode.id)
        self.assertEqual(response.data["title"], "newpromocode")
        self.assertEqual(response.data["discount"], 20)

    def tets_delete_promocode(self):
        response = self.client.put(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(Promocode.objects.filter(id=1).first())

from django.test import TestCase
from t4uApp.models import Promocode, ConcertType, Place, Concerts, SingerVoice, Cart
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

class ConcertTypeTest(TestCase):
    def setUp(self):
        self.concert_type = ConcertType.objects.create(title="Party")

    def test_concert_type_title(self):
        self.assertEqual(str(self.concert_type.title), "Party")

    def test_concert_type_title_max_length(self):
        max_length = self.concert_type._meta.get_field("title").max_length
        self.assertEquals(max_length, 100)


class PlaceTest(TestCase):
    def setUp(self):
        self.place = Place.objects.create(
            address="Minsk", latitude="53.900564", longitude="27.566508"
        )

    def test_place_address(self):
        self.assertEqual(str(self.place.address), "Minsk")

    def test_place_latitude(self):
        self.assertEqual(str(self.place.latitude), "53.900564")

    def test_place_longitude(self):
        self.assertEqual(str(self.place.longitude), "27.566508")

    def test_place_address_max_length(self):
        max_length = self.place._meta.get_field("address").max_length
        self.assertEquals(max_length, 100)

    def test_place_latitude_max_length(self):
        max_length = self.place._meta.get_field("latitude").max_length
        self.assertEquals(max_length, 100)

    def test_place_longitude_max_length(self):
        max_length = self.place._meta.get_field("longitude").max_length
        self.assertEquals(max_length, 100)


class SingerVoiceTest(TestCase):
    def setUp(self):
        self.singer_voice = SingerVoice.objects.create(title="Bas")

    def test_singer_voice_title(self):
        self.assertEqual(str(self.singer_voice.title), "Bas")

    def test_singer_voice_title_max_length(self):
        max_length = self.singer_voice._meta.get_field("title").max_length
        self.assertEquals(max_length, 100)

class ConcertsModelTest(TestCase):
    
    def setUp(self):
        self.place = Place.objects.create(
            address="Minsk", latitude="53.900564", longitude="27.566508"
        )
        self.date_now=timezone.now()

        self.concert_type = ConcertType.objects.create(
            title='Party'
        )
        self.singer_voice = SingerVoice.objects.create(title="Bas")

        self.concert = Concerts.objects.create(
            title='Concert1',
            date=self.date_now,
            placeId=self.place,
            typeId=self.concert_type,
            singerVoiceId=self.singer_voice,
            concertName='ConcertName1',
            composer='Composer1',
            wayHint='WayHint1',
            headliner='Headliner1',
            censor='18',
            poster='poster.jpg',
            desc='Description',
            price=100,
            ticket=50
        )
        
    def test_concert_title(self):
        self.assertEqual(str(self.concert.title), 'Concert1')
        
    def test_concert_date(self):
        self.assertEqual(self.concert.date, self.date_now)
        
    def test_concert_place_id(self):
        self.assertEqual(self.concert.placeId, self.place)
        
    def test_concert_type_id(self):
        self.assertEqual(self.concert.typeId, self.concert_type)
        
    def test_concert_singer_voice_id(self):
        self.assertEqual(self.concert.singerVoiceId, self.singer_voice)
        
    def test_concert_concert_name(self):
        self.assertEqual(str(self.concert.concertName), 'ConcertName1')
        
    def test_concert_composer(self):
        self.assertEqual(str(self.concert.composer), 'Composer1')
        
    def test_concert_way_hint(self):
        self.assertEqual(str(self.concert.wayHint), 'WayHint1')
        
    def test_concert_headliner(self):
        self.assertEqual(str(self.concert.headliner), 'Headliner1')
        
    def test_concert_censor(self):
        self.assertEqual(str(self.concert.censor), '18')
        
    def test_concert_poster(self):
        self.assertEqual(str(self.concert.poster), 'poster.jpg')
        
    def test_concert_desc(self):
        self.assertEqual(str(self.concert.desc), 'Description')
        
    def test_concert_price(self):
        self.assertEqual(self.concert.price, 100)
        
    def test_concert_ticket(self):
        self.assertEqual(self.concert.ticket, 50)        

class PromocodeTest(TestCase):
    def setUp(self):
        self.promocode = Promocode.objects.create(
            title="Promocode1", date=timezone.now(), discount=50
        )

    def test_promocode_title(self):
        self.assertEqual(str(self.promocode.title), "Promocode1")

    def test_promocode_date(self):
        self.assertTrue(self.promocode.date <= timezone.now())

    def test_promocode_discount(self):
        self.assertEqual(self.promocode.discount, 50)

class CartModelTest(TestCase):
    def setUp(self):   
        self.concert = Concerts.objects.create(title="Concert1")
        self.promocode = Promocode.objects.create(title="CODE", discount=10.00)
        self.cart = Cart.objects.create(userId=1, concertId= self.concert, count=2, promocodeId=self.promocode, price=90.00, statusId=1)

    def test_cart(self):
        self.assertEqual(self.cart.userId, 1)
        self.assertEqual(self.cart.concertId, self.concert)
        self.assertEqual(self.cart.count, 2)
        self.assertEqual(self.cart.promocodeId, self.promocode)
        self.assertEqual(self.cart.price, 90.00)
        self.assertEqual(self.cart.statusId, 1)
from rest_framework import serializers
from t4uApp.models.models import Cart


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class CartUserSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='concertId.title')
    poster = serializers.CharField(source='concertId.poster')
    price = serializers.IntegerField(source='concertId.price')
    tickets = serializers.IntegerField(source='concertId.ticket')
    discount = serializers.IntegerField(source='promocodeId.discount', allow_null = True)
    promocode = serializers.CharField(source='promocodeId.title', allow_null = True)

    class Meta:
        model = Cart
        fields = ('id', 'count', 'title', 'poster', 'price', 'tickets', 'discount', 'promocode')    


class CartPaymentSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='concertId.title')    
    price = serializers.IntegerField(source='concertId.price')   
    discount = serializers.IntegerField(source='promocodeId.discount', allow_null = True)   

    class Meta:
        model = Cart
        fields = ('id', 'count', 'title',  'price',  'discount')   
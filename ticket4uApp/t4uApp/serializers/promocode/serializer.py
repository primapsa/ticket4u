from rest_framework import serializers
from t4uApp.models.models import Promocode

class PromocodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocode
        fields = '__all__'
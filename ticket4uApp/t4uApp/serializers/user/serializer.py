from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserSerializerMe(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "is_staff", "id")


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)  

    class Meta:
        model = User       
        fields = ["email", "username", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)    


class TokenLoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)       
        token['is_staff'] = user.is_staff
        token['email'] = user.email
        return token


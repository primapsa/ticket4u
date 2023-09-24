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
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        # fields = ["email", "username", "password", "token"]
        fields = ["email", "username", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    

# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('username', 'password', 'email')
#         extra_kwargs = {'password': {'write_only': True}, }

#     def create(self, validated_data):
#         user = User.objects.create_user(validated_data['username'],
#                                         password=validated_data['password'],
#                                         email=validated_data['email'])
#         return user
    

class TokenLoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)       
        token['is_staff'] = user.is_staff
        token['email'] = user.email
        return token


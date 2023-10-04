import jwt
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from t4uApp.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User


class Me(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializerMe
    queryset = User.objects.all()

    def get(self, request):
        token = request.META.get("HTTP_AUTHORIZATION", " ")
        if not token:
            return Response("", status=status.HTTP_400_BAD_REQUEST)
        token = token.split(" ")[1]
        token = AccessToken(token)
        user_id = token.payload.get("user_id", None)
        if not user_id:
            return Response("", status=status.HTTP_400_BAD_REQUEST)
        user = self.get_user(user_id)
        if not user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(user, context={"request": request})

        return Response(serializer.data, status.HTTP_200_OK)

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None


class SocialLogin(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("jwt", None)
        if not token:
            return Response("", status=status.HTTP_400_BAD_REQUEST)
        decoded = self.decode_token(token)
        if not decoded:
            return Response("", status=status.HTTP_400_BAD_REQUEST)
        email = decoded.get("email")
        first_name = decoded.get("given_name")
        last_name = decoded.get("family_name")

        user = self.get_or_create_user(email, first_name, last_name)
        user_token = self.generate_user_token(user)

        return Response(self._make_output(user_token), status=status.HTTP_200_OK)

    def decode_token(self, token):
        try:
            return jwt.decode(
                token, algorithms=["RS256"], options={"verify_signature": False}
            )
        except jwt.DecodeError:
            return None

    def _make_output(self, token):
        return {"refresh": str(token), "access": str(token.access_token)}

    def get_or_create_user(self, email, first_name, last_name):
        user = User.objects.filter(username=email).first()

        if not user:
            user = User(
                username=email, first_name=first_name, last_name=last_name, email=email
            )
            user.save()
        return user

    def generate_user_token(self, user):
        return TokenLoginSerializer.get_token(user)


class Register(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(
            "Пользователь уже существует", status=status.HTTP_400_BAD_REQUEST
        )


class TokenLogin(TokenObtainPairView):
    serializer_class = TokenLoginSerializer


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


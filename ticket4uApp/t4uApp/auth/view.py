import jwt
from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializer import RegisterSerializer, UserSerializer, MyTokenObtainPairSerializer
from .. import setting


class RegisterApi(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    
    def post(self, request, *args,  **kwargs):        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()      
            return Response(serializer.data, status.HTTP_200_OK)
        return Response('Пользователь уже существует', status=status.HTTP_400_BAD_REQUEST)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

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

class SocialLoginAuth(APIView):
    def post(self, request):
        print(request)
        if not request.data['jwt']:
            return Response(status.HTTP_400_BAD_REQUEST)
        user = jwt.decode(request['jwt'], settings.SECRET_KEY, algorithms=["HS256"])
        print(user)



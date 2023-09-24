"""
URL configuration for ticket4uApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import sys
sys.path.append("..")
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView
)

from t4uApp.auth.view import MyTokenObtainPairView
from t4uApp.auth.view import RegisterApi, SocialLoginAuth
from t4uApp import views
from t4uApp import views2

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('api/concerts/', views2.ConcertList.as_view()),
                  path('api/concerts/<int:pk>', views2.ConcertDetail.as_view()),
                  path('api/type/', views2.ConcertTypeList.as_view()),
                  path('api/voice/', views2.SingerVoiceList.as_view()),                
                  path('api/promocodes/', views2.PromocodeList.as_view()),
                #   path('api/promocodes/<str:pk>', views.promocode_change),
                  path('api/promocodes/<str:pk>', views2.PromocodeDetail.as_view()),
                  path('api/promocode/', views2.PromocodeCardDetail.as_view()),
                  path('api/cart/', views2.CartList.as_view()),
                  path('api/cart/<str:pk>', views2.CartDetail.as_view()),
                  path('api/cart/user/<str:uid>', views2.CartUserDetail.as_view()),
                  path('api/webhook/paypal/', views2.Paypal.as_view()),
                  path('api/paypal/create/', views2.Payment.as_view()),             
                  path('api/user/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
                  path('api/user/login/social/', views2.SocialLogin.as_view()),
                  path('api/user/register/', RegisterApi.as_view()),
                  path('api/user/me/', views2.Me.as_view()),
                  path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
                  path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),   
                  path('test/<int:pk>/', views.CartDetail.as_view()),             
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

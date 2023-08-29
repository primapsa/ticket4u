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
from t4uApp.auth.view import RegisterApi
from t4uApp import views

urlpatterns = [
                  path('admin/', admin.site.urls),
                  re_path(r'^api/concerts/$', views.concert_list),
                  re_path(r'^api/type/$', views.concert_type),
                  re_path(r'^api/voice/$', views.singer_voice),
                  path('api/concerts/<str:pk>', views.concert),
                  path('api/promocodes/', views.promocode_list),
                  path('api/promocodes/<str:pk>', views.promocode_change),
                  path('api/promocode/', views.promocode_find),
                  path('api/cart/', views.cart_list),
                  path('api/cart/<str:pk>', views.cart_change),
                  path('api/cart/user/<str:uid>', views.cart_user),
                  path('api/webhook/paypal/', views.paypal),
                  path('api/paypal/create/', views.make_payment2),
                  path('api/paypal/create_2/', views.make_payment2),
                  path('api/paypal/create_3/', views.make_3),
                  path('api/user/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
                  path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
                  path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
                  # path('api/users/', views.RegistrationAPIView.as_view())
                  path('api/user/register/', RegisterApi.as_view()),
                  path('api/user/me/', views.me),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

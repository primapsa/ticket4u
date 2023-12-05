from django.urls import path
from t4uApp import views


urlpatterns = [
    path('', views.CartList.as_view()),
    path('<str:pk>', views.CartDetail.as_view()),
    path('user/<str:uid>', views.CartUserDetail.as_view())
]

               
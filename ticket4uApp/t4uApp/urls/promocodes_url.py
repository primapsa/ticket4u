from django.urls import path
from t4uApp import views 

urlpatterns = [
    path('', views.PromocodeList.as_view()),                
    path('<str:pk>', views.PromocodeDetail.as_view()),
]
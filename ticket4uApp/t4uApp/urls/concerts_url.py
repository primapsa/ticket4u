from django.urls import path
from t4uApp import views 

urlpatterns = [
    path('', views.ConcertList.as_view()),
    path('<int:pk>', views.ConcertDetail.as_view()),
]
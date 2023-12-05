from django.urls import path
from t4uApp import views 

urlpatterns = [
    path('webhook/', views.Paypal.as_view()),
    path('create/', views.Payment.as_view())
]
from django.urls import path
from t4uApp import views


urlpatterns = [
    path('refresh/', views.TokenRefreshView.as_view()),
    path('verify/', views.TokenVerifyView.as_view()),
]
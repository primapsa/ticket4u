from django.urls import path
from t4uApp import views 

urlpatterns = [
    path('login/social/', views.SocialLogin.as_view()),
    path('register/', views.Register.as_view()),
    path('login/', views.TokenLogin.as_view()),
    path('me/', views.Me.as_view()),
]
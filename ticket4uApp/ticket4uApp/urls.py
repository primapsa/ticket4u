import sys

sys.path.append("..")
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from t4uApp import views
from t4uApp.urls import *

urlpatterns = [
    path("api/v1/concerts/", include(concerts_url)),
    path("api/v1/type/", views.ConcertTypeList.as_view()),
    path("api/v1/voice/", views.SingerVoiceList.as_view()), 
    path("api/v1/promocode/", views.PromocodeCardDetail.as_view()),
    path("api/v1/promocodes/", include(promocodes_url)),
    path("api/v1/paypal/", include(paypal_url)),
    path("api/v1/cart/", include(cart_url)),
    path("api/v1/user/", include(user_url)),
    path("api/v1/token/", include(token_url)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

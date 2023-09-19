from django.urls import path
from ..views import user_join, login, check_id

urlpatterns = [
    path("join/", user_join),
    path("login/", login),
    path("checkid/", check_id),
]

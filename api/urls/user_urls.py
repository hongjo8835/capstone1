from django.urls import path
from ..views import user_join, login, check_id

urlpatterns = [
    path("user/join/", user_join),
    path("user/login/", login),
    path("user/checkid/", check_id),
]

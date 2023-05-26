from django.urls import path
from . import views


urlpatterns = [
    # path("", views.index),
    # path("apicall/", views.apicall),
    path("barnumretrun/", views.barnum_return),
    path("join/", views.user_join),
    path("login/", views.login),
    path("get/", views.get_foodlist_info),
]

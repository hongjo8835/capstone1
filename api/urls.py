from django.urls import path
from . import views


urlpatterns = [
    path("barnumretrun/", views.barnum_return),
    path("join/", views.user_join),
    path("login/", views.login),
    path("get/", views.get_foodlist_info),
    path("putingredient/", views.put_ingredient),
    path("checkid/", views.check_id),
    path("delingredients/", views.delete_ingredients),
    path("update_ingredient/", views.update_ingredient)
]

from django.urls import path
from ..views import barnum_return, get_foodlist_info, put_ingredient, delete_ingredients, update_ingredient

urlpatterns = [
    path("barnumretrun/", barnum_return),
    path("get/", get_foodlist_info),
    path("put_ingredient/", put_ingredient),
    path("del_ingredients/", delete_ingredients),
    path("updt_ingredient/", update_ingredient),
]

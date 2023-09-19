from django.urls import path
from ..views import barnum_return, get_foodlist_info, put_ingredient, delete_ingredients, update_ingredient

urlpatterns = [
    path("food/barnumretrun/", barnum_return),
    path("food/get/", get_foodlist_info),
    path("food/putingredient/", put_ingredient),
    path("food/delingredients/", delete_ingredients),
    path("food/update_ingredient/", update_ingredient),
]

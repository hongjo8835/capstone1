from django.urls import path
from ..views import barnum_return, get_foodlist_info, put_ingredient, delete_ingredients, update_ingredient, recipe_recommendation, get_recipe_detail

urlpatterns = [
    path("barnumretrun/", barnum_return),
    path("get/", get_foodlist_info),
    path("put_ingredient/", put_ingredient),
    path("del_ingredients/", delete_ingredients),
    path("updt_ingredient/", update_ingredient),
    path('recommend/', recipe_recommendation),
    path('recipe_detail/<str:recipe_name>/', get_recipe_detail)
]

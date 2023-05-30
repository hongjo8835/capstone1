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
    path("update_ingredient/", views.update_ingredient),
    path("create_post/", views.create_post),
    path("update_post/<int:board_id>/", views.update_post),
    path("list_post/", views.list_posts),
    path("get_post/<int:board_id>/", views.get_post),
    path("del_post/<int:board_id>/", views.delete_post),
]

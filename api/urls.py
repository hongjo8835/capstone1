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
    path("post/list_post/", views.list_posts),
    path("post/get_post/<int:board_id>/", views.get_post),
    path("post/create_post/", views.create_post),
    path("post/update_post/<int:board_id>/", views.update_post),
    path("post/del_post/<int:board_id>/", views.delete_post),
    path("post/get_post/<int:board_id>/comments/", views.create_comment),
    path("post/del_comment/<int:comment_id>/", views.delete_comment),
    path("post/<int:board_id>/comment/<int:comment_id>/update/", views.update_comment)

]

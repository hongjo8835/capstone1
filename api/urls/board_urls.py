from django.urls import path
from ..views import list_posts, get_post, create_post, update_post, delete_post,create_comment, delete_comment, update_comment

urlpatterns = [
    path("post/list_post/", list_posts),
    path("post/get_post/<int:board_id>/", get_post),
    path("post/create_post/", create_post),
    path("post/update_post/<int:board_id>/", update_post),
    path("post/del_post/<int:board_id>/", delete_post),
    path("post/get_post/<int:board_id>/comments/", create_comment),
    path("post/del_comment/<int:comment_id>/", delete_comment),
    path("post/<int:board_id>/comment/<int:comment_id>/update/", update_comment),
]

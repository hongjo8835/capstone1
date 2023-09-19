from django.urls import path, include
from . import views


urlpatterns = [
    path('post/', include('api.urls.board_urls')),
    path('food/', include('api.urls.food_urls')),
    path('user/', include('api.urls.user_urls')),

]

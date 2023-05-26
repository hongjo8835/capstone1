from rest_framework import serializers
from .models import Board, FoodList, Comment
from django.contrib.auth import get_user_model


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['userid', 'username', 'password', 'email']
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['userid', 'username', 'password', 'email']


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'


class FoodListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodList
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

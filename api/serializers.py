from rest_framework import serializers
from .models import Board, FoodList, Comment, User
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

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            userid=validated_data['userid']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

    def get_replies(self, comment):
        if comment.parent_comment is None:
            return CommentSerializer(comment.replies.all(), many=True).data
        return None


class BoardSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['title', 'user', 'content', 'date', 'comments']


class FoodListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodList
        fields = '__all__'

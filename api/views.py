import os
import urllib.request
from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
# from argon2 import PasswordHasher
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import BoardSerializer, UserSerializer, FoodListSerializer
from .models import Board, User, FoodList


# Create your views here.


@csrf_exempt
@require_POST
def barnum_return(request):
    received_data = json.loads(request.body)
    barnum = received_data.get('barnum', "")
    client_secret = os.getenv("API_KEY")
    url = "http://openapi.foodsafetykorea.go.kr/api/" + client_secret + "/C005/json/1/1/BAR_CD=" + barnum
    api_request = urllib.request.Request(url)
    # api_request.add_header("api_secret", client_secret)
    # api_request.add_header("barnum", barnum)
    response = urllib.request.urlopen(api_request)
    rescode = response.getcode()
    if (rescode == 200):
        response_body = response.read()
        result = json.loads(response_body.decode("utf-8"))
        # items = result.get('items')
        #
        # context = {
        #     'items': items
        # }
        # decode_data = result
        return JsonResponse(result, safe=False)
    else:
        context = {"api": "fail"}
        return JsonResponse(context)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def user_join(request):
    password = request.data.get('password')
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        user.set_password(password)
        user.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    userid = request.data.get('userid')
    password = request.data.get('password')

    user = authenticate(userid=userid, password=password)
    if user is None:
        return Response({'message': '아이디 또는 비밀번호가 일치하지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    update_last_login(None, user)

    return Response({'refresh_token': str(refresh),
                     'access_token': str(refresh.access_token), }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_foodlist_info(request):
    authentication = JWTAuthentication()
    user, _ = authentication.authenticate(request)

    if user is None:
        return Response({'message': '인증되지 않은 사용자입니다.'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        food_data = FoodList.objects.filter(user_id=user.id)
        serializer = FoodListSerializer(food_data, many=True)
        # user_data = User.objects.get(userid=user.userid)
        # serializer = UserSerializer(user_data)
        return JsonResponse(serializer.data, safe=False)
    except FoodList.DoesNotExist:
        context = {"foodlist": "does not exist"}
        return JsonResponse(context)



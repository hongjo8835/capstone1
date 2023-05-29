import os
import urllib.request

from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json
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
    response = urllib.request.urlopen(api_request)
    rescode = response.getcode()
    if (rescode == 200):
        response_body = response.read()
        result = json.loads(response_body.decode("utf-8"))
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
        context = {"status": "success"}
        return Response(context, status=status.HTTP_201_CREATED)
    else:
        context = {"status": "fail"}
        return Response(context, status=status.HTTP_400_BAD_REQUEST)


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
@permission_classes([IsAuthenticated])
def get_foodlist_info(request):
    user = request.user

    if user is None:
        return Response({'message': '인증되지 않은 사용자입니다.'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        food_data = FoodList.objects.filter(user_id=user.id)
        serializer = FoodListSerializer(food_data, many=True)
        return JsonResponse(serializer.data, safe=False)
    except FoodList.DoesNotExist:
        context = {"foodlist": "does not exist"}
        return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def put_ingredient(request):
    user = request.user

    if user is None:
        return Response({'message': '인증되지 않은 사용자입니다.'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        food_data = request.data.get('foodlist', [])
        serializer = FoodListSerializer(data=food_data, many=True)
        if serializer.is_valid():
            # DB에 저장
            food_list = serializer.save(user=user)
            saved_food_data = FoodListSerializer(food_list, many=True).data
            return JsonResponse(saved_food_data, safe=False, status=status.HTTP_201_CREATED)
        else:
            # 실패한 경우, 오류 메시지를 반환합니다.
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except FoodList.DoesNotExist:
        context = {"foodlist": "does not exist"}
        return JsonResponse(context)


import os
import urllib.request
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json

from api.models import BarcodeData, FoodList
from api.serializers import FoodListSerializer


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def barnum_return(request):
    received_data = json.loads(request.body)
    barnum = received_data.get('barnum', "")

    try:
        barcode_data = BarcodeData.objects.get(barnum=barnum)
        if timezone.now() - barcode_data.created_at > timedelta(minutes=5):
            raise BarcodeData.DoesNotExist

        result = barcode_data.data
    except BarcodeData.DoesNotExist:
        client_secret = os.getenv("API_KEY")
        url = "http://openapi.foodsafetykorea.go.kr/api/" + client_secret + "/C005/json/1/1/BAR_CD=" + barnum
        api_request = urllib.request.Request(url)
        response = urllib.request.urlopen(api_request)
        res_code = response.getcode()

        if res_code == 200:
            response_body = response.read()
            result = json.loads(response_body.decode("utf-8"))
            BarcodeData.objects.update_or_create(barnum=barnum, defaults={'data': result})
            return JsonResponse(result, safe=False)

        else:
            context = {"api": "fail"}
            return JsonResponse(context)

    return JsonResponse(result, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_foodlist_info(request):
    user = request.user

    if user is None:
        return Response({'message': '인증되지 않은 사용자입니다.'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        food_data = FoodList.objects.filter(user_id=user.id).order_by('date')
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
            saved_food_data = {"foodlist": FoodListSerializer(food_list, many=True).data}
            return JsonResponse(saved_food_data, safe=False, status=status.HTTP_201_CREATED)

        else:
            # 실패한 경우, 오류 메시지를 반환합니다.
            return JsonResponse(serializer.errors, safe=False, status=status.HTTP_400_BAD_REQUEST)
    except FoodList.DoesNotExist:
        context = {"foodlist": "does not exist"}
        return JsonResponse(context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_ingredients(request):
    user = request.user
    ingredient_ids = request.data.get('ingredient_ids', [])

    if isinstance(ingredient_ids, int):
        ingredient_ids = [ingredient_ids]

    valid_ingredients = FoodList.objects.filter(id__in=ingredient_ids, user=user)

    if not valid_ingredients.exists():
        return Response({"message": "Failed to delete ingredients. No matching items found."},
                        status=status.HTTP_400_BAD_REQUEST)

    deleted_ingredient_ids = [ingredient.id for ingredient in valid_ingredients]
    deleted_count = valid_ingredients.delete()

    if deleted_count[0] > 0:
        return Response(
            {"message": f"{deleted_count[0]} ingredients deleted.", "deleted_ingredient_ids": deleted_ingredient_ids},
            status=status.HTTP_200_OK)
    else:
        return Response({"message": "Failed to delete ingredients."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_ingredient(request):
    user = request.user
    data = request.data
    ingredient_id = data.get('id')

    # ID 값 확인
    if not ingredient_id:
        return JsonResponse({"message": "Ingredient ID is missing."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        ingredient = FoodList.objects.get(pk=ingredient_id, user=user)
    except ObjectDoesNotExist:
        return JsonResponse({"message": "Ingredient not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = FoodListSerializer(ingredient, data=data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    else:
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
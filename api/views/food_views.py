import os
import urllib.request
from datetime import timedelta
import pickle
import urllib.parse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
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
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recipe_recommendation(request):
    user = request.user
    if user is None:
        return Response({'message': '인증되지 않은 사용자입니다.'}, status=status.HTTP_401_UNAUTHORIZED)
    # 현재 로그인한 사용자의 FoodList를 가져옵니다.
    try:
        food_data = FoodList.objects.filter(user_id=user.id)
        # 각 식품 이름을 쉼표로 연결하여 하나의 문자열로 만듭니다.
        user_input = ', '.join([food_item.name for food_item in food_data])


        
    except FoodList.DoesNotExist:
        context = {"foodlist": "does not exist"}
        return JsonResponse(context)
    

    # 디스크에서 모델 로드 (상대 경로나 절대 경로를 적절히 사용하세요)
    model_filename = os.path.join(os.path.dirname(__file__), '..', '..', 'recipe_file', 'bkm_model.pkl')
    loaded_model = pickle.load(open(model_filename, 'rb'))

    # 디스크에서 vectorizer 로드 (상대 경로나 절대 경로를 적절히 사용하세요)
    vectorizer_filename = os.path.join(os.path.dirname(__file__), '..', '..', 'recipe_file','tfidf_vectorizer.pkl')
    vectorizer = pickle.load(open(vectorizer_filename, 'rb'))

    # TF-IDF Vectorizer로 사용자 입력 변환 
    user_input_vector = vectorizer.transform([user_input])

    # 사용자 입력에 대한 클러스터 라벨 예측
    predicted_cluster = loaded_model.predict(user_input_vector)

    df_no_space_filepath = os.path.join(os.path.dirname(__file__), '..', '..','recipe_file', '레시피 데이터_공백제거.csv')  # 적절한 파일 경로 설정하기

    df_no_space= pd.read_csv(df_no_space_filepath , encoding='utf-8')

    df_cleaned_filepath = os.path.join(os.path.dirname(__file__), '..', '..','recipe_file', 'cleaned_레시피 데이터.csv')  # 적절한 파일 경로 설정하기

    df_cleaned= pd.read_csv(df_cleaned_filepath , encoding='utf-8')

    # 'rcp_parts_dtls_cleaned' 열에서 NaN 값을 가진 행 삭제
    df_cleaned = df_cleaned.dropna(subset=['rcp_parts_dtls_cleaned'])

    
    # 'predicted_labels.pkl'에서 예측된 클러스터 라벨 로드
    labels_filename = os.path.join(os.path.dirname(__file__), '..', '..', 'recipe_file', 'predicted_labels.pkl')
    with open(labels_filename, 'rb') as f:
        predicted_labels = pickle.load(f)

    # df_cleaned DataFrame에 cluster_label 열 추가
    df_cleaned['cluster_label'] = predicted_labels

    # 사용자 입력에 대해 예측된 클러스터의 모든 레시피 찾기
    cluster_recipes = df_cleaned[df_cleaned['cluster_label'] == predicted_cluster[0]]

    recipe_scores = []
    for _, recipe_row in cluster_recipes.iterrows():
        recipe_vector = vectorizer.transform([recipe_row['rcp_parts_dtls_cleaned']])

        user_input_vector_adjusted = user_input_vector.copy()
        recipe_vector_adjusted = recipe_vector.copy()

        user_tokens = user_input.split(',')
        for token in user_tokens:
            token_index = vectorizer.vocabulary_.get(token.strip())
            if token_index is not None:
                user_input_vector_adjusted[0, token_index] *= 2

        score= cosine_similarity(user_input_vector_adjusted ,recipe_vector_adjusted )[0][0]
        matching_recipe_in_no_space_df= df_no_space[df_no_space['RCP_NM'] == recipe_row['RCP_NM']]
        if len(matching_recipe_in_no_space_df) > 0:
            rcp_nm_to_display= matching_recipe_in_no_space_df.iloc[0]['RCP_NM']
        else:
            rcp_nm_to_display= recipe_row['RCP_NM']

        recipe_scores.append((rcp_nm_to_display ,score))

    # 예측 점수가 높은 순으로 정렬합니다.
    recipe_scores.sort(key=lambda x: x[1], reverse=True)

    recommended_recipes=[]
    for rcp_nm, score in recipe_scores[:5]:
        matching_recipe_in_no_space_df = df_no_space[df_no_space['RCP_NM'] == rcp_nm]
        if len(matching_recipe_in_no_space_df) > 0:
            image_link = matching_recipe_in_no_space_df.iloc[0]['ATT_FILE_NO_MK']
        else:
            image_link = "No recipe found"

        recommended_recipes.append({"RCP_NM": rcp_nm, "image_link": image_link})

    return JsonResponse({"recipes": recommended_recipes})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recipe_detail(request, recipe_name):
    # 로그인된 사용자 확인
    user = request.user
    if user is None:
        return Response({'message': '인증되지 않은 사용자입니다.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # CSV 파일 경로
    df_no_space_filepath = os.path.join(os.path.dirname(__file__), '..', '..','recipe_file', '레시피 데이터_공백제거.csv')  

    df_no_space = pd.read_csv(df_no_space_filepath , encoding='utf-8')

    # URL 디코딩
    recipe_name_decoded = urllib.parse.unquote(recipe_name)

    # 레시피 이름에서 공백 제거
    recipe_name_no_space = recipe_name_decoded.replace(" ", "")

    # 레시피 이름으로 데이터를 찾습니다.
    df_no_space['RCP_NM_no_space'] = df_no_space['RCP_NM'].str.replace(" ", "")
    matching_recipe_data = df_no_space[df_no_space['RCP_NM_no_space'] == recipe_name_no_space]

    # 일치하는 레시피가 없는 경우
    if len(matching_recipe_data) == 0:
        return JsonResponse({'message': '해당 레시피를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

    # 일치하는 레시피가 있는 경우, 해당 레시피의 상세 정보를 반환합니다.
    recipe_detail = matching_recipe_data.to_dict(orient='records')[0]
    
    # 'ATT_FILE_NO_MK' 필드 제거
    recipe_detail.pop('ATT_FILE_NO_MK', None)
    recipe_detail.pop('RCP_SEQ', None)
    recipe_detail.pop('RCP_NM_no_space', None)

    return JsonResponse(recipe_detail)    
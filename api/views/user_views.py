from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import User
from api.serializers import UserSerializer


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def user_join(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()
        context = {"status": "success"}
        return Response(context, status=status.HTTP_201_CREATED)
    else:
        context = {"status": "fail"}
        return Response(context, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def check_id(request):
    userid = request.data.get('userid')
    result = {"status": "fail"}
    if userid:
        user = User.objects.filter(userid=userid)
        if user.exists():
            result = {
                "status": "fail"
            }
            return JsonResponse(result, status=400)  # 중복된 아이디인 경우 400
        else:
            result = {
                "status": "success"
            }
    return JsonResponse(result)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    userid = request.data.get('userid')
    password = request.data.get('password')

    user = authenticate(userid=userid, password=password)
    if user is None:
        return Response({'status': '아이디 또는 비밀번호가 일치하지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    update_last_login(None, user)

    return Response({'refresh_token': str(refresh),
                     'access_token': str(refresh.access_token), }, status=status.HTTP_200_OK)
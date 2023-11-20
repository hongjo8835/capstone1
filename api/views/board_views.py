from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.models import Board, Comment
from api.serializers import BoardSerializer, CommentSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    user = request.user

    if user is None:
        return Response({'message': '인증되지 않은 사용자입니다.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        board_data = request.data
        serializer = BoardSerializer(data=board_data)
        if serializer.is_valid():
            # DB에 저장
            post = serializer.save(user=user)
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # 실패한 경우, 오류 메시지를 반환합니다.
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_post(request, board_id):
    user = request.user

    if user is None:
        return Response({'message': '인증되지 않은 사용자입니다.'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        # 전달된 post_id에 해당하는 게시글을 가져옵니다.
        board = Board.objects.get(pk=board_id, user=user)

        # 요청 데이터로 게시글을 업데이트합니다.
        serializer = BoardSerializer(board, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Board.DoesNotExist:
        return Response({"message": "게시물이 없습니다."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_posts(request):
    # 데이터베이스에서 모든 게시글 가져오기
    posts = Board.objects.all()
    # 게시글 시리얼라이징
    serializer = BoardSerializer(posts, many=True)
    # JSON 응답 반환
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_post(request, board_id):
    try:
        # 데이터베이스에서 지정된 게시글 가져오기
        post = Board.objects.get(pk=board_id)

        # 게시글 시리얼라이징
        serializer = BoardSerializer(post)

          # JSON 응답 반환
        return JsonResponse(serializer.data)

    except Board.DoesNotExist:
        return Response({"message": "게시물이 없습니다."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_post(request, board_id):
    try:
        # 데이터베이스에서 지정된 게시글 가져오기
        board = Board.objects.get(pk=board_id)

        # 게시글 작성자와 요청 사용자가 일치하는 경우 게시글을 삭제합니다.
        if board.user == request.user:
            board.delete()
            return JsonResponse({'message': '게시글이 정상적으로 삭제되었습니다.'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': '다른 사용자의 게시글은 삭제할 수 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    except Board.DoesNotExist:
        return Response({"message": "게시물이 없습니다."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment(request, board_id):
    board = Board.objects.get(pk=board_id)
    data = request.data.copy()
    data['board'] = board.id
    data['user'] = request.user.id
    serializer = CommentSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    # 작성자와 로그인 사용자가 동일하지 않으면 삭제 거부
    if comment.user != request.user:
        return Response({"message": "다른 사용자의 게시글은 삭제할 수 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    comment.delete()
    return Response({"message": "게시글이 정상적으로 삭제되었습니다."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_comment(request, board_id, comment_id):
    board = Board.objects.get(pk=board_id)
    comment = Comment.objects.get(pk=comment_id)

    if request.user.id != comment.user.id:
        return Response({'message': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    data = request.data.copy()
    data['board'] = board.id
    data['user'] = request.user.id

    serializer = CommentSerializer(comment, data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

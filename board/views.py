from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from board.serializers import BoardSerializer, BoardCommentSerializer
from board.models import Board as BoardModel, BoardComment,  BoardLike as BoardLikeModel
# Create your views here.

class BoardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        all_board_list = BoardModel.objects.all().order_by('-create_date')
        return Response({
            "boards" : BoardSerializer(all_board_list, many=True).data}
            
        ,status=status.HTTP_200_OK)

    def post(self, request):
        try:
            request.data['author'] = request.user.id
            create_board_serializer = BoardSerializer(data = request.data)
            create_board_serializer.is_valid(raise_exception=True)
            create_board_serializer.save()
            return Response({"message" : "게시글이 생성되었습니다."}, status=status.HTTP_200_OK)
        except:
            return Response({"message" : "저장에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, board_id):
        update_board = BoardModel.objects.get(id=board_id)
        update_board_serializer = BoardSerializer(update_board, data=request.data, partial = True)
        update_board_serializer.is_valid(raise_exception=True)
        update_board_serializer.save()
        return Response({
            "message" : "게시글이 수정되었습니다."
        },status=status.HTTP_200_OK)

    def delete(self, request, board_id):
        delete_board = BoardModel.objects.get(id=board_id)
        if delete_board:
            delete_board.delete()
            return Response({"message": "게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        return Response({"message": "삭제에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)


class BorderLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, board_id):
        author = request.user
        target_board = BoardModel.objects.get(id=board_id)
        liked_board, created = BoardLikeModel.objects.get_or_create(author = author, board=target_board)
        if created:
            liked_board.save()
            return Response({"message": "좋아요가 완료 되었습니다!!"}, status=status.HTTP_200_OK)
        liked_board.delete()
        return Response({"message": "좋아요가 취소 되었습니다!!"}, status=status.HTTP_200_OK)


class BorderCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        all_board_list = BoardComment.objects.all().order_by('-create_date')
        return Response({
            "boards" : BoardCommentSerializer(all_board_list, many=True).data}
            
        ,status=status.HTTP_200_OK)

    def post(self, request, obj_id):
        #obj_id는 board_id 입니다.
        try:
            request.data['author'] = request.user.id
            request.data['board'] = obj_id
            create_board_comment_serializer = BoardCommentSerializer(data = request.data)
            create_board_comment_serializer.is_valid(raise_exception=True)
            create_board_comment_serializer.save()
            print(create_board_comment_serializer.errors)
            return Response({"message" : "댓글이 생성되었습니다."}, status=status.HTTP_200_OK)
        except:
            return Response({"message" : "저장에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)

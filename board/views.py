from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from board.serializers import BoardSerializer
from board.models import Board as BoardModel
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
            return Response(create_board_serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(create_board_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, board_id):
        update_board = BoardModel.objects.get(id=board_id)
        update_board_serializer = BoardSerializer(update_board, data=request.data, partial = True)
        update_board_serializer.is_valid(raise_exception=True)
        update_board_serializer.save()
        return Response({
            "message" : "수정이 완료 되었습니다."
        },status=status.HTTP_200_OK)

    def delete(self, request, board_id):
        delete_board = BoardModel.objects.get(id=board_id)
        if delete_board:
            delete_board.delete()
            return Response({"message": "게시물 삭제"}, status=status.HTTP_200_OK)
        return Response({"message": "삭제할 게시물이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)


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
    


    def post(self, request):
        try:
            request.data['author'] = request.user.id
            board_serializer = BoardSerializer(data = request.data)
            board_serializer.is_valid(raise_exception=True)
            board_serializer.save()
            return Response(board_serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(board_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from worry_board.models import WorryBoard as WorryBoardModel
from worry_board.serializers import WorryBoardSerializer
# Create your views here.

class WorryBoardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        all_board_list = WorryBoardModel.objects.all().order_by("-create_date")
        return Response(
            {"boards": WorryBoardSerializer(all_board_list, many=True, context={"request" : request}).data,},
            status=status.HTTP_200_OK,
        )
    
    def post(self, request):
        request.data["author"] = request.user.id
        create_worry_board_serializer = WorryBoardSerializer(data = request.data)
        if create_worry_board_serializer.is_valid(raise_exception=True):
            create_worry_board_serializer.save()
            return Response({"message": "고민을 게시하였습니다."}, status=status.HTTP_200_OK)
        else :
            return Response({"message": "게시에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)
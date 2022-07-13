from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.db.models.query_utils import Q

from .serializers import (
    LetterReviewSerializer,
    UserProfileSerializer,
    LetterSerilaizer
)
from .models import WorryCategory
from worry_board.serializers import WorryBoardSerializer
from worry_board.models import WorryBoard as WorryBoardModel


# Create your views here.
class MainPageView(APIView):
    """
    메인 페이지의 CRUD를 담당하는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):

        cur_user =request.user
        profile_grade= request.user.userprofile.mongle_grade
        letter_count = request.user.userlettertargetuser_set.all().count()
        worry_list = WorryBoardModel.objects.none()
        for cate_get in WorryCategory.objects.all():
            worry_list = worry_list.union(WorryBoardModel.objects.filter(category=cate_get).order_by("-create_date")[:3])

        return Response(
            {
                "profile_grade": profile_grade,
                "letter_count": letter_count,
                "rank_list": UserProfileSerializer(cur_user).data,
                "worry_list": WorryBoardSerializer(worry_list, many=True).data,
                "reviews" : LetterReviewSerializer(cur_user).data
            },
            status=status.HTTP_200_OK,
        )

class LetterView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    """
    Letter CRUD 를 담당하는 view 
    """
    def post(self, request):

        worry_board_get = request.data['worry_board_id']
        request.data['letter_author'] = request.user.id
        request.data['category'] = WorryBoardModel.objects.get(id=worry_board_get).category.id
        letterserialzier = LetterSerilaizer(data=request.data)
        letterserialzier.is_valid(raise_exception=True)
        letterserialzier.save(worryboard=WorryBoardModel.objects.get(id=worry_board_get))
        return Response({"messge"},status=status.HTTP_200_OK)

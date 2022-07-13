from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.db.models.query_utils import Q

from .serializers import LetterReviewSerializer
from .serializers import UserProfileSerializer
from .serializers import LetterSerilaizer
from worry_board.serializers import WorryBoardSerializer
from worry_board.models import WorryBoard as WorryBoardModel
from .models import Letter as LetterModel

# Create your views here.
class MainPageView(APIView):
    """
    메인 페이지의 CRUD를 담당하는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        cur_user = request.user
        review_get = LetterReviewModel.objects.none()
        profile_grade = request.user.userprofile.mongle_grade

        cur_user = request.user
        profile_grade = request.user.userprofile.mongle_grade
        letter_count = request.user.userlettertargetuser_set.all().count()
        worry_list = []
        for cate_get in range(1, 7):
            worry_gets = WorryBoardModel.objects.filter(category=cate_get).order_by(
                "-create_date"
            )[:3]
            for worry_get in worry_gets:
                cate = {
                    "worry_id": worry_get,
                    "category": worry_get.category,
                    "content": worry_get.content,
                }
                worry_list.append(cate)
        return Response(
            {
                "profile_grade": profile_grade,
                "letter_count": letter_count,
                "rank_list": UserProfileSerializer(cur_user).data,
                "worry_list": WorryBoardSerializer(worry_list, many=True).data,
                "reviews": LetterReviewSerializer(cur_user).data,
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
        letter_author = request.user
        title = request.data["title"]
        content = request.data["content"]
        worry_board_get = request.data["worry_board_id"]
        category = WorryBoardModel.objects.get(id=worry_board_get).category.id
        post_datas = {
            "category": category,
            "letter_author": letter_author.id,
            "title": title,
            "content": content,
            "worryboard": worry_board_get,
        }
        letterserialzier = LetterSerilaizer(data=post_datas)
        letterserialzier.is_valid(raise_exception=True)
        letterserialzier.save()
        return Response({"messge"}, status=status.HTTP_200_OK)

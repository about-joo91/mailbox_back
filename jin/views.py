from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import MaiapageSerializer
from .serializers import LetterSerializer
from .models import LetterReview as LetterReviewModel
from worry_board.models import WorryBoard

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

        return Response(
            {
                "profile_grade": profile_grade,
                "main_datas": MaiapageSerializer(review_get).data,
                "letter_count": LetterSerializer(cur_user).data,
            },
            status=status.HTTP_200_OK,
        )

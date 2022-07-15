from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from worry_board.models import WorryBoard as WorryBoardModel
from worry_board.serializers import WorryBoardSerializer

from .models import LetterReview as LetterReviewModel
from .models import LetterReviewLike as LetterReviewLikeModel
from .models import WorryCategory
from .serializers import LetterReviewSerializer, LetterSerilaizer, UserProfileSerializer

# Create your views here.


class ReviewLikeView(APIView):
    """
    메인페이지 리뷰 Like 를 담당하는 기능
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, board_id):
        author = request.user
        target_board = LetterReviewModel.objects.get(id=board_id)
        liked_board, created = LetterReviewLikeModel.objects.get_or_create(
            user_id=author, review_id=target_board
        )
        if created:
            liked_board.save()
            return Response({"message": "좋아요가 완료 되었습니다!!"}, status=status.HTTP_200_OK)
        liked_board.delete()
        return Response({"message": "좋아요가 취소 되었습니다!!"}, status=status.HTTP_200_OK)


class MainPageView(APIView):
    """
    메인 페이지의 CRUD를 담당하는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        cur_user = request.user
        profile_grade = request.user.userprofile.mongle_grade
        letter_count = request.user.userlettertargetuser_set.all().count()
        worry_list = WorryBoardModel.objects.none()
        for cate_get in WorryCategory.objects.all():
            worry_list = worry_list.union(
                WorryBoardModel.objects.filter(category=cate_get).order_by(
                    "-create_date"
                )[:3]
            )

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

        worry_board_get = request.data["worry_board_id"]
        request.data["letter_author"] = request.user.id
        request.data["category"] = WorryBoardModel.objects.get(
            id=worry_board_get
        ).category.id
        letterserialzier = LetterSerilaizer(data=request.data)
        letterserialzier.is_valid(raise_exception=True)
        letterserialzier.save(
            worryboard=WorryBoardModel.objects.get(id=worry_board_get)
        )
        return Response({"messge"}, status=status.HTTP_200_OK)

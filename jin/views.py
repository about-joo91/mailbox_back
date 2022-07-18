from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from unsmile_filtering import pipe
from worry_board.models import WorryBoard as WorryBoardModel
from worry_board.serializers import WorryBoardSerializer

from . import recommender
from .models import Letter as LetterModel
from .models import LetterReview as LetterReviewModel
from .models import LetterReviewLike as LetterReviewLikeModel
from .models import WorryCategory
from .serializers import (
    BestReviewSerializer,
    LetterSerilaizer,
    LiveReviewSerializer,
    UserProfileSerializer,
)

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
        best_review_list = LetterReviewModel.objects.all().order_by("-grade")[:3]
        live_review_list = LetterReviewModel.objects.all().order_by("-create_date")[:2]
        profile_grade = request.user.userprofile.mongle_grade

        profile_image = request.user.userprofile.profile_img
        my_worry_get = WorryBoardModel.objects.filter(author=request.user)
        letter_count = LetterModel.objects.filter(
            worryboard__id__in=my_worry_get
        ).count()

        # 가장 최근에 편지를 썼던 워리보드 아이디 기반 추천
        user_letters = LetterModel.objects.filter(letter_author=cur_user).order_by(
            "-create_date"
        )[:1]
        latest_worryboard_id = [obj.worryboard.id for obj in user_letters][0]
        recomendation_sys = recommender.recommend_worryboard
        final_worryboard_list = recomendation_sys.recommend_worries(
            latest_worryboard_id
        )

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
                "porfile_image": profile_image,
                "letter_count": letter_count,
                "rank_list": UserProfileSerializer(cur_user).data,
                "recommend_list": WorryBoardSerializer(
                    final_worryboard_list, many=True
                ).data,
                "worry_list": WorryBoardSerializer(worry_list, many=True).data,
                "best_review": BestReviewSerializer(
                    best_review_list, context={"request": request}, many=True
                ).data,
                "live_review": LiveReviewSerializer(
                    live_review_list, context={"request": request}, many=True
                ).data,
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
        result = pipe(request.data["content"])[0]
        print(result)
        if result["label"] == "clean":
            worry_board_get = request.data["worry_board_id"]
            request.data["letter_author"] = request.user.id
            letterserialzier = LetterSerilaizer(data=request.data)
            letterserialzier.is_valid(raise_exception=True)
            letterserialzier.save(
                worryboard=WorryBoardModel.objects.get(id=worry_board_get)
            )
            return Response({"message"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

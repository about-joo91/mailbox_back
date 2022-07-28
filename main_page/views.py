import math

import django
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

import unsmile_filtering
from main_page.services.letter_service import (
    letter_is_read_service,
    letter_post_service,
    letter_review_like_delete_service,
    letter_review_like_service,
)
from main_page.services.main_gage_service import (
    best_review_list_service,
    live_review_list_service,
    my_letter_count,
    worry_worryboard_union,
)
from user.models import User as UserModel
from worry_board.serializers import WorryBoardSerializer

from . import recommender
from .models import Letter as LetterModel
from .models import WorryCategory as WorryCategoryModel
from .serializers import (
    BestReviewSerializer,
    LiveReviewSerializer,
    MainPageDataSerializer,
)


# Create your views here.


class ReviewLikeView(APIView):
    """
    메인페이지 리뷰 Like 를 담당하는 기능
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, letter_review_id):
        try:
            letter_review_like_service(
                letter_review_id=letter_review_id, user_id=request.user.id
            )
            return Response(
                {
                    "detail": "좋아요가 완료 되었습니다!!",
                },
                status=status.HTTP_200_OK,
            )
        except django.db.utils.IntegrityError:
            return Response(
                {
                    "detail": "좋아요를 이미 누르셨습니다!!",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, letter_review_id):
        letter_review_like_delete_service(
            letter_review_id=letter_review_id, user_id=request.user.id
        )
        return Response(
            {
                "detail": "좋아요가 취소 되었습니다!!",
            },
            status=status.HTTP_200_OK,
        )


class LikeisGet(APIView):
    """
    Review 좋아요 누를시 get을 통해서
    실시간으로 랭킹 업데이트
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        return Response(
            {
                "best_review": BestReviewSerializer(
                    best_review_list_service(), context={"request": request}, many=True
                ).data,
                "live_review": LiveReviewSerializer(
                    live_review_list_service(), context={"request": request}, many=True
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class MainPageView(APIView):
    """
    메인 페이지의 CRUD를 담당하는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        cur_user = request.user

        latest_user_letter = LetterModel.objects.filter(letter_author=cur_user).order_by(
            "-create_date"
        )[:1][0]
        worryboard_id_of_letter = latest_user_letter.worryboard.id
        recomendation_sys = recommender.recommend_worryboard
        final_worryboard_list = recomendation_sys.recommend_worries(
            worryboard_id_of_letter
        )
        not_read_my_letter_count = my_letter_count(request.user.id)

        worry_categories = WorryCategoryModel.objects.prefetch_related(
            "worryboard_set"
        ).all()
        order_by_cate_worry_list = worry_worryboard_union(worry_categories)
        user_profile_data = {}
        try:
            user_profile_data = MainPageDataSerializer(
                UserModel.objects.select_related("userprofile").get(id=cur_user.id)
            ).data
        except UserModel.userprofile.RelatedObjectDoesNotExist:
            return Response(
                {"detail": "유저프로필이 없습니다 생성해주세요."}, status=status.HTTP_404_NOT_FOUND
            )

        grade_order_best_reviews = best_review_list_service()
        create_order_live_reviews = live_review_list_service()
        return Response(
            {
                "letter_count": not_read_my_letter_count,
                "user_profile_data": user_profile_data,
                "order_by_cate_worry_list": WorryBoardSerializer(
                    order_by_cate_worry_list, context={"request": request}, many=True
                ).data,
                "best_review": BestReviewSerializer(
                    grade_order_best_reviews, context={"request": request}, many=True
                ).data,
                "live_review": LiveReviewSerializer(
                    create_order_live_reviews, context={"request": request}, many=True
                ).data,
                "recommend_worry_board_list": WorryBoardSerializer(
                    final_worryboard_list, context={"request": request}, many=True
                ),
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
        data_content = request.data["content"]
        repeat_num = math.ceil(len(data_content) / 900)
        filtering_sys = unsmile_filtering.post_filtering
        for i in range(repeat_num):
            result = filtering_sys.unsmile_filter(data_content[900 * i : 900 * (i + 1)])
            if result["label"] != "clean":
                return Response(
                    {"detail": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            break
        try:
            letter_post_service(letter_author=request.user, request_data=request.data)
            return Response({"detail": "편지 작성이 완료 되었습니다."}, status=status.HTTP_200_OK)
        except django.db.utils.IntegrityError:
            return Response(
                {"detail": "이미 편지를 작성 하셨습니다."}, status=status.HTTP_400_BAD_REQUEST
            )


class LetterisReadView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    """
    Letter is_read 를 담당하는 view
    """

    def post(self, request, letter_id):

        letter_is_read_service(letter_id)
        return Response(status=status.HTTP_200_OK)

import math

import django
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

import unsmile_filtering
from jin.services.letter_service import (
    letter_is_read_service,
    letter_post_service,
    letter_review_like_service,
)
from jin.services.main_gage_service import (
    best_review_list_service,
    live_review_list_service,
    worry_obj_my_letter,
    worry_worryboard_union,
)
from worry_board.models import WorryBoard as WorryBoardModel
from worry_board.serializers import WorryBoardSerializer

from . import recommender
from .models import Letter as LetterModel
from .models import WorryCategory as WorryCategoryModel
from .serializers import (
    BestReviewSerializer,
    LiveReviewSerializer,
    MainPageDataSerializer,
)

# from . import recommender


# Create your views here.


class ReviewLikeView(APIView):
    """
    메인페이지 리뷰 Like 를 담당하는 기능
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, letter_review_id):
        if letter_review_like_service(
            letter_review_id=letter_review_id, user_id=request.user.id
        ):
            return Response(
                {
                    "message": "좋아요가 완료 되었습니다!!",
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "좋아요가 취소 되었습니다!!",
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

        # 가장 최근에 편지를 썼던 워리보드 아이디 기반 추천
        # user_letters = LetterModel.objects.filter(letter_author=cur_user).order_by(
        #     "-create_date"
        # )[:1]
        # latest_worryboard_id = [obj.worryboard.id for obj in user_letters][0]
        # recomendation_sys = recommender.recommend_worryboard
        # final_worryboard_list = recomendation_sys.recommend_worries(
        #     latest_worryboard_id
        # )

        my_worrys = worry_obj_my_letter(request.user.id)
        letter_count = 0
        for letter_get in my_worrys:
            try:
                if letter_get.letter.is_read == False:
                    letter_count += 1
            except WorryBoardModel.letter.RelatedObjectDoesNotExist:
                break

        worry_categorys = WorryCategoryModel.objects.prefetch_related(
            "worryboard_set"
        ).all()
        worry_list = worry_worryboard_union(worry_categorys)

        return Response(
            {
                "letter_count": letter_count,
                "user_profile_data": MainPageDataSerializer(cur_user).data,
                "worry_list": WorryBoardSerializer(worry_list, many=True).data,
                "best_review": BestReviewSerializer(
                    best_review_list_service(), context={"request": request}, many=True
                ).data,
                "live_review": LiveReviewSerializer(
                    live_review_list_service(), context={"request": request}, many=True
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
        data_content = request.data["content"]
        repeat_num = math.ceil(len(data_content) / 900)
        filtering_sys = unsmile_filtering.post_filtering
        for i in range(repeat_num):
            result = filtering_sys.unsmile_filter(data_content[900 * i : 900 * (i + 1)])
            if result["label"] != "clean":
                return Response(
                    {"message": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            break
        try:
            worry_board_get = request.data["worry_board_id"]
            request.data["letter_author"] = request.user.id
            letter_post_service(
                worry_board_id=worry_board_get, request_data=request.data
            )
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

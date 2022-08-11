import math

import django
from django.core.cache import cache
from rest_framework import exceptions, status
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
    main_page_data_and_user_profile,
    my_letter_count,
    worry_worryboard_union,
)
from user.models import User as UserModel
from worry_board.serializers import WorryBoardSerializer

from .models import Letter as LetterModel
from .models import LetterReviewLike as LetterReviewLikeModel
from .serializers import BestReviewSerializer, LiveReviewSerializer

# Create your views here.


class ReviewLikeView(APIView):
    """
    메인페이지 리뷰 Like 를 담당하는 기능
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, letter_review_like_id):
        try:
            letter_review_like_service(letter_review_id=letter_review_like_id, user_id=request.user.id)
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

    def delete(self, request, letter_review_like_id) -> Response:
        try:
            letter_review_like_delete_service(letter_review_like_id=letter_review_like_id, user_id=request.user.id)
            return Response(
                {
                    "detail": "좋아요가 취소 되었습니다!!",
                },
                status=status.HTTP_200_OK,
            )
        except LetterReviewLikeModel.DoesNotExist:
            return Response({"detail": "없는 리뷰 입니다."}, status=status.HTTP_400_BAD_REQUEST)
        except exceptions.PermissionDenied:
            return Response(
                {"detail": "이 작업을 수행할 권한(permission)이 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
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

        try:
            main_page_data_and_user_profile_data = main_page_data_and_user_profile(cur_user.id)
        except UserModel.userprofile.RelatedObjectDoesNotExist:
            return Response({"detail": "유저프로필이 없습니다 생성해주세요."}, status=status.HTTP_404_NOT_FOUND)
        except UserModel.monglegrade.RelatedObjectDoesNotExist:
            return Response(
                {"detail": "몽글그레이드 정보가 없습니다 생성해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        not_read_my_letter_count = my_letter_count(cur_user.id)
        order_by_cate_worry_list = worry_worryboard_union()
        grade_order_best_reviews = best_review_list_service()
        create_order_live_reviews = live_review_list_service()

        return Response(
            {
                "letter_count": not_read_my_letter_count,
                "main_page_data_and_user_profile": main_page_data_and_user_profile_data,
                "order_by_cate_worry_list": WorryBoardSerializer(
                    order_by_cate_worry_list, context={"author": cur_user}, many=True
                ).data,
                "best_review": BestReviewSerializer(
                    grade_order_best_reviews, context={"request": request}, many=True
                ).data,
                "live_review": LiveReviewSerializer(
                    create_order_live_reviews, context={"request": request}, many=True
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
                    {"detail": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            break
        try:
            letter_post_service(letter_author=request.user, request_data=request.data)
            return Response({"detail": "편지 작성이 완료 되었습니다."}, status=status.HTTP_200_OK)
        except django.db.utils.IntegrityError:
            return Response({"detail": "이미 편지를 작성 하셨습니다."}, status=status.HTTP_400_BAD_REQUEST)


class LetterisReadView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    """
    Letter is_read 를 담당하는 view
    """

    def post(self, request, letter_id):
        try:
            letter_is_read_service(letter_id=letter_id, user_id=request.user.id)
            return Response(status=status.HTTP_200_OK)

        except LetterModel.DoesNotExist:
            return Response({"detail": "자신이 받은 편지가 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)


class AllCacheDelete(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    """
    로그 아웃시 모든 캐시를 삭제
    """

    def post(self, request):

        cache.delete("live_reviews")
        cache.delete("best_reviews")
        cache.delete("my_letter_count")
        cache.delete("my_boards_data"), cache.delete("boards_data")
        cache.delete("cate_paginated_worry_boards"), cache.delete("all_paginated_worry_boards")
        for i in range(1, 7):
            cache.delete(f"{i}_paginated_worry_boards")

        return Response(status=status.HTTP_200_OK)

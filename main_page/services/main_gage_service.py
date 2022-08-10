from django.core.cache import cache
from django.db.models.query_utils import Q

from main_page.models import Letter as LetterModel
from main_page.models import LetterReview as LetterReviewModel
from main_page.models import WorryCategory as WorryCategoryModel
from main_page.serializers import MainPageDataSerializer
from user.models import User as UserModel
from worry_board.models import WorryBoard as WorryBoardModel


def main_page_data_and_user_profile(user_id: int) -> list[dict]:

    """
    메인 페이지에 유저데이터및 유저프로필을 가져오기 위한 service
    """
    if not cache.get("main_profile_data"):
        main_page_data_and_user_profile = {}
        main_page_data_and_user_profile = MainPageDataSerializer(
            UserModel.objects.select_related("userprofile").get(id=user_id)
        ).data
        cache.set("main_profile_data", main_page_data_and_user_profile, 60 * 60)

    return cache.get("main_profile_data")


def my_letter_count(user_id: int) -> list[dict]:
    """
    메인 페이지에 읽은 편지 개수를 가져오기 위한 service
    """

    if not cache.get("my_letter_count"):

        my_worrys = LetterModel.objects.filter(Q(is_read=False) & Q(worryboard__author=user_id)).count()

        cache.set("my_letter_count", my_worrys)

    return cache.get("my_letter_count")


def worry_worryboard_union() -> list[dict]:
    """
    메인페이지 카테고리별로 3개씩 게시물을 가져오기 위한 service
    """

    if not cache.get("worry_worryboard_union"):

        worry_categories = WorryCategoryModel.objects.prefetch_related("worryboard_set").all()
        order_by_cate_worry_list = WorryBoardModel.objects.none()
        for cate_idx in range(worry_categories.count()):
            order_by_cate_worry_list = order_by_cate_worry_list.union(
                worry_categories[cate_idx].worryboard_set.order_by("-create_date")[:3]
            )
        cache.set("worry_worryboard_union", order_by_cate_worry_list)

    return cache.get("worry_worryboard_union")


def best_review_list_service() -> list[dict]:
    """
    메인페이지 베스트리뷰 게시물을 가져오기 위한 service
    """

    if not cache.get("best_reviews"):
        best_reviews_data = LetterReviewModel.objects.order_by("-like_count").order_by("-grade")[:10]

        cache.set("best_reviews", best_reviews_data)

    return cache.get("best_reviews")


def live_review_list_service() -> list[dict]:
    """
    메인페이지 라이브리뷰 게시물을 가져오기 위한 service
    """

    if not cache.get("live_reviews"):
        live_reviews_data = LetterReviewModel.objects.order_by("-create_date")[:10]

        cache.set("live_reviews", live_reviews_data)

    return cache.get("live_reviews")

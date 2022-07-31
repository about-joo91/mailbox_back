from django.db.models.query_utils import Q
from django.http import HttpResponse

from recommendation import recommender
from main_page.models import Letter as LetterModel
from main_page.models import LetterReview as LetterReviewModel
from worry_board.models import WorryBoard as WorryBoardModel


def my_letter_count(user_id: int) -> list[dict]:
    """
    메인 페이지에 읽은 편지 개수를 가져오기 위한 service
    """
    my_worrys = LetterModel.objects.filter(Q(is_read=False) & Q(worryboard__author=user_id)).count()

    return my_worrys


def worry_worryboard_union(worry_categorys: list[dict]) -> list[dict]:
    """
    메인페이지 카테고리별로 3개씩 게시물을 가져오기 위한 service
    """
    order_by_cate_worry_list = WorryBoardModel.objects.none()
    for cate_idx in range(worry_categorys.count()):
        order_by_cate_worry_list = order_by_cate_worry_list.union(
            worry_categorys[cate_idx].worryboard_set.order_by("-create_date")[:3]
        )

    return order_by_cate_worry_list


def best_review_list_service():
    """
    메인페이지 베스트리뷰 게시물을 가져오기 위한 service
    """

    return LetterReviewModel.objects.all().order_by("-grade")[:10]


def live_review_list_service():
    """
    메인페이지 라이브리뷰 게시물을 가져오기 위한 service
    """
    return LetterReviewModel.objects.all().order_by("-create_date")[:10]


def recommend_worryboard_list(cur_user : object):
    """
    추천시스템 service
    """
    try:
        latest_user_letter = LetterModel.objects.filter(letter_author=cur_user).order_by(
            "-create_date"
        )[:1]
        worryboard_id_of_letter = latest_user_letter[0].worryboard.id
        recomendation_sys = recommender.recommend_worryboard
        final_worryboard_list = recomendation_sys.recommend_worries(
            worryboard_id_of_letter, cur_user
        )
        return final_worryboard_list
    
    except IndexError:
        print("네가 쓴 편지가 없어서 키에러!!")
        return HttpResponse(status=204)


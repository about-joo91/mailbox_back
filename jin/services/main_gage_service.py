from jin.models import LetterReview as LetterReviewModel
from worry_board.models import WorryBoard
from worry_board.models import WorryBoard as WorryBoardModel


def worry_obj_my_letter(user_id: int) -> list[dict]:
    """
    메인 페이지에 읽은 편지 개수를 가져오기 위한 service
    """
    return WorryBoard.objects.filter(author_id=user_id).select_related("letter")


def worry_worryboard_union(worry_categorys: list) -> list[dict]:
    """
    메인페이지 카테고리별로 3개씩 게시물을 가져오기 위한 service
    """
    worry_list = WorryBoardModel.objects.none()
    for cate_idx in range(worry_categorys.count()):
        worry_list = worry_list.union(
            worry_categorys[cate_idx].worryboard_set.order_by("-create_date")[:3]
        )
    return worry_list


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

from django.db.models import F
from main_page.models import Letter as LetterModel
from main_page.models import LetterReview as LetterReviewModel
from main_page.models import LetterReviewLike as LetterReviewLikeModel
from main_page.serializers import LetterSerilaizer
from worry_board.models import WorryBoard as WorryBoardModel


def letter_post_service(worry_board_id: int, request_data: dict) -> None:
    """
    편지 보내는 기능을 담당하는 service
    """
    letterserialzier = LetterSerilaizer(data=request_data)
    letterserialzier.is_valid(raise_exception=True)
    letterserialzier.save(worryboard=WorryBoardModel.objects.get(id=worry_board_id))


def letter_is_read_service(letter_id) -> None:
    """
    유저가 받은 편지 읽음 post 를 담당하는 service
    """
    letter = LetterModel.objects.filter(id=letter_id)
    letter.update(is_read=True)


def letter_review_like_service(letter_review_id: int, user_id: int) -> None:
    """
    편지 리뷰의 라이크를 담당하는 service
    """
    target_board = LetterReviewModel.objects.get(id=letter_review_id)
    like_create = LetterReviewLikeModel.objects.create(
        user_id=user_id, letter_review=target_board
        )
    if like_create:
        LetterReviewModel.objects.filter(id=letter_review_id).update(
        grade=F("grade") + 100
    )


def letter_review_like_delete_service(letter_review_id: int, user_id: int) -> None:
    """
    편지 리뷰의 라이크 삭제 를 담당하는 service
    """
    target_board = LetterReviewModel.objects.get(
        id=letter_review_id
        )
    like_delete = LetterReviewLikeModel.objects.filter(
        letter_review_id=target_board.id,
        user_id=user_id
        ).delete()
    if like_delete:
        LetterReviewModel.objects.filter(id=letter_review_id).update(
        grade= F("grade")- 100
    )


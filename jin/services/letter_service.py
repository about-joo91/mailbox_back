from jin.models import Letter as LetterModel
from jin.models import LetterReview as LetterReviewModel
from jin.models import LetterReviewLike as LetterReviewLikeModel
from jin.serializers import LetterSerilaizer
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


def letter_review_like_service(letter_review_id: int, user_id: int) -> bool:
    """
    편지 리뷰의 라이크를 담당하는 service
    """
    target_board = LetterReviewModel.objects.get(id=letter_review_id)
    liked_board, created = LetterReviewLikeModel.objects.get_or_create(
        user_id=user_id, letter_review=target_board
    )
    if created:
        LetterReviewModel.objects.filter(id=letter_review_id).update(
            grade=target_board.grade + 100
        )

    else:
        liked_board.delete()
        LetterReviewModel.objects.filter(id=letter_review_id).update(
            grade=target_board.grade - 100
        )

    return created

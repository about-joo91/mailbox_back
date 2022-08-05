from django.db import transaction
from django.db.models import F
from django.db.models.query_utils import Q
from rest_framework import exceptions

from main_page.models import Letter as LetterModel
from main_page.models import LetterReview as LetterReviewModel
from main_page.models import LetterReviewLike as LetterReviewLikeModel
from main_page.serializers import LetterSerilaizer
from my_page.services.letter_review_service import update_mongle_grade
from user.models import User as UserModel
from worry_board.models import WorryBoard as WorryBoardModel


@transaction.atomic
def letter_post_service(letter_author: UserModel, request_data: dict) -> None:
    """
    편지 보내는 기능을 담당하는 service
    """
    worry_board_id = request_data.pop("worry_board_id")
    worry_board = WorryBoardModel.objects.select_related("author").get(id=worry_board_id)
    letterserialzier = LetterSerilaizer(data=request_data)
    letterserialzier.is_valid(raise_exception=True)
    letterserialzier.save(worryboard=worry_board, letter_author=letter_author)

    letter_author.sent_letter_cnt = F("sent_letter_cnt") + 1
    letter_author.save()

    worry_board.author.received_letter_cnt = F("received_letter_cnt") + 1
    worry_board.author.save()

    update_mongle_grade(letter_author=letter_author, grade=1, rate_type="letter")


def letter_is_read_service(letter_id: LetterModel, user_id=UserModel) -> None:
    """
    유저가 받은 편지 읽음 post 를 담당하는 service
    """

    letter = LetterModel.objects.filter(Q(id=letter_id) & Q(worryboard__author=user_id))
    if not letter:
        raise LetterModel.DoesNotExist

    letter.update(is_read=True)


@transaction.atomic
def letter_review_like_service(letter_review_id: int, user_id: int) -> None:
    """
    편지 리뷰의 라이크를 담당하는 service
    """
    target_board = LetterReviewModel.objects.get(id=letter_review_id)
    like_create = LetterReviewLikeModel.objects.create(user_id=user_id, letter_review=target_board)
    if like_create:
        LetterReviewModel.objects.filter(id=letter_review_id).update(like_count=F("like_count") + 1)


@transaction.atomic
def letter_review_like_delete_service(letter_review_like_id: int, user_id: int) -> None:
    """
    편지 리뷰의 라이크 삭제 를 담당하는 service
    """

    target_review_like = LetterReviewLikeModel.objects.get(id=letter_review_like_id)

    if target_review_like.user.id != user_id:
        raise exceptions.PermissionDenied
    LetterReviewModel.objects.filter(id=target_review_like.letter_review.id).update(like_count=F("like_count") - 1)
    target_review_like.delete()

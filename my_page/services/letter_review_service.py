from bisect import bisect_left

from django.db import transaction
from django.db.models import F

from main_page.models import Letter as LetterModel
from main_page.models import LetterReview
from my_page.serializers import LetterReviewSerializer
from user.models import MongleGrade, MongleLevel
from user.models import User as UserModel

MONGLE_GRADE_RATE = {"review": 10, "letter": 100, "board": 5}
MONGLE_GRADE_BISECTS = [199, 599, 1199, 2499]


def update_mongle_grade(user: UserModel, grade: int, rate_type: str) -> None:
    MongleGrade.objects.filter(user=user).update(grade=F("grade") + (grade * MONGLE_GRADE_RATE[rate_type]))

    refreshed_user = UserModel.objects.select_related("monglegrade__mongle_level").get(id=user.id)
    cur_grade = refreshed_user.monglegrade.grade
    cur_level = update_mongle_level(cur_grade=cur_grade)

    if refreshed_user.monglegrade.mongle_level_id == cur_level:
        return
    refreshed_user.monglegrade.mongle_level = MongleLevel.objects.get(id=cur_level)
    refreshed_user.monglegrade.save()


def update_mongle_level(cur_grade: int) -> int:
    return bisect_left(MONGLE_GRADE_BISECTS, cur_grade) + 1


@transaction.atomic
def create_letter_review(user: UserModel, letter_id: int, review_data: dict[str, str]) -> None:
    target_letter = (
        LetterModel.objects.select_related("worryboard__author")
        .select_related("letter_author__monglegrade")
        .get(id=letter_id)
    )
    if target_letter.worryboard.author == user:
        letter_review_serializer = LetterReviewSerializer(data=review_data)
        letter_review_serializer.is_valid(raise_exception=True)

        letter_author = target_letter.letter_author
        update_mongle_grade(user=letter_author, grade=int(review_data["grade"]), rate_type="review")
        letter_review_serializer.save(review_author=user, letter=target_letter)
    else:
        raise PermissionError


def edit_letter_review(user: UserModel, letter_review_id: int, edit_data: dict[str, str]) -> None:
    cur_letter_review = LetterReview.objects.get(id=letter_review_id)
    if cur_letter_review.review_author == user:
        letter_review_serializer = LetterReviewSerializer(cur_letter_review, data=edit_data, partial=True)
        letter_review_serializer.is_valid(raise_exception=True)
        letter_review_serializer.save()
    else:
        raise PermissionError


def delete_letter_review(user: UserModel, letter_review_id: int) -> None:
    cur_letter_review = (
        LetterReview.objects.select_related("letter").select_related("letter__letter_author").get(id=letter_review_id)
    )
    if cur_letter_review.review_author == user:
        past_grade = cur_letter_review.grade * -1
        letter_author = cur_letter_review.letter.letter_author
        update_mongle_grade(user=letter_author, grade=past_grade, rate_type="review")
        cur_letter_review.delete()
    else:
        raise PermissionError

from main_page.models import Letter as LetterModel
from main_page.models import LetterReview
from my_page.serializers import LetterReviewSerializer
from user.models import User


def make_letter_review(user: User, letter_id: int, review_data: dict[str, str]) -> None:
    target_letter = LetterModel.objects.get(id=letter_id)
    letter_review_serializer = LetterReviewSerializer(data=review_data)
    letter_review_serializer.is_valid(raise_exception=True)
    letter_review_serializer.save(review_author=user, letter=target_letter)


def edit_letter_review(user: User, letter_review_id: int, edit_data: dict[str, str]) -> None:
    cur_letter_review = LetterReview.objects.get(id=letter_review_id)
    if cur_letter_review.review_author == user:
        letter_review_serializer = LetterReviewSerializer(cur_letter_review, data=edit_data, partial=True)
        letter_review_serializer.is_valid(raise_exception=True)
        letter_review_serializer.save()
    else:
        raise PermissionError


def delete_letter_review(user: User, letter_review_id: int) -> None:
    cur_letter_review = LetterReview.objects.get(id=letter_review_id)
    if cur_letter_review.review_author == user:
        cur_letter_review.delete()
    else:
        raise PermissionError

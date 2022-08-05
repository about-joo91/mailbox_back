from django.db import IntegrityError
from django.test import TestCase
from rest_framework import exceptions

from main_page.models import Letter as LetterModel
from main_page.models import LetterReview as LetterReviewModel
from main_page.models import LetterReviewLike as LetterReivewLikeModel
from main_page.models import WorryCategory as WorryCategoryModel
from main_page.services.letter_service import (
    letter_is_read_service,
    letter_post_service,
    letter_review_like_delete_service,
    letter_review_like_service,
)
from main_page.services.main_gage_service import my_letter_count
from user.models import User as UserModel
from worry_board.models import WorryBoard as WorryBoardModel


class TestLoginUser(TestCase):
    def test_letter_post_service(self) -> None:
        """
        편지 보내는 함수 검증
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
        author = UserModel.objects.create(username="author", nickname="author")

        worry_cate_obj = WorryCategoryModel.objects.create(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(author_id=user.id, content="ttttt", category_id=worry_cate_obj.id)

        request_data = {
            "title": "제목입니다",
            "content": "내용입니다",
            "worry_board_id": worry_obj.id,
        }

        letter_post_service(letter_author=author, request_data=request_data)

        self.assertEqual(1, UserModel.objects.get(id=user.id).received_letter_cnt)
        self.assertEqual(1, UserModel.objects.get(id=author.id).sent_letter_cnt)
        self.assertEqual(
            author.id,
            LetterModel.objects.get(letter_author_id=author.id).letter_author.id,
        )
        self.assertEqual(
            worry_obj.id,
            LetterModel.objects.get(letter_author_id=author.id).worryboard.id,
        )
        self.assertEqual("제목입니다", LetterModel.objects.get(letter_author_id=author.id).title)
        self.assertEqual("내용입니다", LetterModel.objects.get(letter_author_id=author.id).content)

    def test_when_none_worry_to_letter_post_service(self) -> None:
        """
        편지 보내는 함수 검증
        case: 없는 worryborad 에 편지를 보낼경우
        """
        UserModel.objects.create(username="hajin", nickname="hajin")
        author = UserModel.objects.create(username="author", nickname="author")

        WorryCategoryModel.objects.create(cate_name="일상")

        request_data = {
            "title": "제목입니다",
            "content": "내용입니다",
            "worry_board_id": 9999,
        }
        request_data["letter_author"] = author.id

        with self.assertRaises(WorryBoardModel.DoesNotExist):
            letter_post_service(letter_author=author, request_data=request_data)

    def test_when_letter_overlap_post_service(self) -> None:
        """
        편지 보내는 함수 검증
        case: 같은 worryborad로 편지를 보낼 때
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
        author = UserModel.objects.create(username="author", nickname="author")

        worry_cate_obj = WorryCategoryModel.objects.create(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(author_id=user.id, content="ttttt", category_id=worry_cate_obj.id)

        request_data = {
            "title": "제목입니다",
            "content": "내용입니다",
            "worry_board_id": worry_obj.id,
        }
        over_lap_request_data = {
            "title": "제목입니다",
            "content": "내용입니다",
            "worry_board_id": worry_obj.id,
        }
        with self.assertRaises(IntegrityError):
            letter_post_service(letter_author=author, request_data=request_data)
            letter_post_service(letter_author=author, request_data=over_lap_request_data)

    def test_letter_is_read_service(self) -> None:
        """
        내가 받은 편지 읽음 여부를 확인하는 함수 검증
        case : is_read 를 통해 letter_count 가 제대로 나오는지.
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
        author = UserModel.objects.create(username="author", nickname="author")
        worry_cate_obj = WorryCategoryModel.objects.create(cate_name="일상")

        worry_obj = WorryBoardModel.objects.create(author_id=user.id, content="ttttt", category_id=worry_cate_obj.id)
        WorryBoardModel.objects.create(author_id=user.id, content="ttttt", category_id=worry_cate_obj.id)

        letter_obj = LetterModel.objects.create(
            letter_author_id=author.id,
            worryboard_id=worry_obj.id,
            title="test",
            content="tist",
        )

        letter_is_read_service(letter_id=letter_obj.id, user_id=user.id)

        self.assertEqual(0, my_letter_count(user_id=user.id))

    def test_when_letter_does_not_exist__letter_is_read_service(self) -> None:
        """
        내가 받은 편지 읽음 여부를 확인하는 함수 검증
        case: 자신이 받은 편지가 아닐 경우
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
        author = UserModel.objects.create(username="author", nickname="author")
        worry_cate_obj = WorryCategoryModel.objects.create(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(author_id=user.id, content="ttttt", category_id=worry_cate_obj.id)
        WorryBoardModel.objects.create(author_id=user.id, content="ttttt", category_id=worry_cate_obj.id)
        letter_obj = LetterModel.objects.create(
            letter_author_id=author.id,
            worryboard_id=worry_obj.id,
            title="test",
            content="tist",
        )

        with self.assertRaises(LetterModel.DoesNotExist):
            letter_is_read_service(letter_id=letter_obj.id, user_id=9999)

    def test_letter_review_like_service(self) -> None:
        """
        편지 리뷰 좋아요 함수 검증
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
        author = UserModel.objects.create(username="author", nickname="author")
        worry_cate_obj = WorryCategoryModel.objects.create(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(author_id=user.id, content="ttttt", category_id=worry_cate_obj.id)
        letter_obj = LetterModel.objects.create(
            letter_author_id=author.id,
            worryboard_id=worry_obj.id,
            title="test",
            content="tist",
        )
        letter_review_obj = LetterReviewModel.objects.create(
            review_author_id=user.id, letter_id=letter_obj.id, grade=100, content="test"
        )

        letter_review_like_service(letter_review_id=letter_review_obj.id, user_id=user.id)

        self.assertEqual(
            letter_review_obj.id,
            LetterReivewLikeModel.objects.get(letter_review_id=letter_review_obj.id).letter_review.id,
        )
        self.assertEqual(user.id, LetterReivewLikeModel.objects.get(user_id=user.id).user.id)
        self.assertEqual(1, LetterReviewModel.objects.get(id=letter_review_obj.id).like_count)

    def test_then_not_valid_letter_review_like_service(self) -> None:
        """
        편지 리뷰 좋아요 함수 검증
        case : 편지 리뷰가  유효하지 않을 경우
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
        author = UserModel.objects.create(username="author", nickname="author")
        worry_cate_obj = WorryCategoryModel.objects.create(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(author_id=user.id, content="ttttt", category_id=worry_cate_obj.id)
        LetterModel.objects.create(
            letter_author_id=author.id,
            worryboard_id=worry_obj.id,
            title="test",
            content="tist",
        )

        with self.assertRaises(LetterReviewModel.DoesNotExist):
            letter_review_like_service(letter_review_id=9999, user_id=user.id)

    def test_thne_like_user_not_valid_letter_review_like_service(self) -> None:
        """
        편지 리뷰 좋아요 함수 검증
        case : 좋아요를 누른 유저가 유효하지 않을 경우
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
        author = UserModel.objects.create(username="author", nickname="author")
        worry_cate_obj = WorryCategoryModel.objects.create(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(author_id=user.id, content="ttttt", category_id=worry_cate_obj.id)
        letter_obj = LetterModel.objects.create(
            letter_author_id=author.id,
            worryboard_id=worry_obj.id,
            title="test",
            content="tist",
        )
        letter_review_obj = LetterReviewModel.objects.create(
            review_author_id=user.id, letter_id=letter_obj.id, grade=100, content="test"
        )

        with self.assertRaises(IntegrityError):
            letter_review_like_service(letter_review_id=letter_review_obj.id, user_id=9999)

    def test_letter_review_like_delete_service(self) -> None:
        """
        편지 리뷰 좋아요 삭제 함수 검증
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
        author = UserModel.objects.create(username="author", nickname="author")
        worry_cate_obj = WorryCategoryModel.objects.create(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(author_id=user.id, content="ttttt", category_id=worry_cate_obj.id)
        letter_obj = LetterModel.objects.create(
            letter_author_id=author.id,
            worryboard_id=worry_obj.id,
            title="test",
            content="tist",
        )
        letter_review_obj = LetterReviewModel.objects.create(
            review_author_id=user.id, letter_id=letter_obj.id, grade=100, content="test"
        )

        letter_review_like_service(letter_review_id=letter_review_obj.id, user_id=user.id)
        letter_review_like_service(letter_review_id=letter_review_obj.id, user_id=author.id)

        target = LetterReivewLikeModel.objects.get(user_id=user.id)

        letter_review_like_delete_service(letter_review_like_id=target.id, user_id=user.id)

        self.assertEqual(
            letter_review_obj.id,
            LetterReivewLikeModel.objects.get(letter_review_id=letter_review_obj.id).letter_review.id,
        )
        self.assertEqual(author.id, LetterReivewLikeModel.objects.get(user_id=author.id).user.id)
        self.assertEqual(1, LetterReviewModel.objects.get(id=letter_review_obj.id).like_count)

    def test_when_none_review_letter_review_like_delete_service(self) -> None:
        """
        편지 리뷰 좋아요 삭제 함수 검증
        case: 없는 리뷰에 삭제를 요청 할 경우
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
        author = UserModel.objects.create(username="author", nickname="author")
        worry_cate_obj = WorryCategoryModel.objects.create(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(author_id=user.id, content="ttttt", category_id=worry_cate_obj.id)
        letter_obj = LetterModel.objects.create(
            letter_author_id=author.id,
            worryboard_id=worry_obj.id,
            title="test",
            content="tist",
        )
        letter_review_obj = LetterReviewModel.objects.create(
            review_author_id=user.id, letter_id=letter_obj.id, grade=100, content="test"
        )

        letter_review_like_service(letter_review_id=letter_review_obj.id, user_id=user.id)

        with self.assertRaises(LetterReivewLikeModel.DoesNotExist):
            letter_review_like_delete_service(letter_review_like_id=9999, user_id=user.id)

    def test_when_different_user_review_like_delete_service(self) -> None:
        """
        편지 리뷰 좋아요 삭제 함수 검증
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
        author = UserModel.objects.create(username="author", nickname="author")
        worry_cate_obj = WorryCategoryModel.objects.create(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(author_id=user.id, content="ttttt", category_id=worry_cate_obj.id)
        letter_obj = LetterModel.objects.create(
            letter_author_id=author.id,
            worryboard_id=worry_obj.id,
            title="test",
            content="tist",
        )
        letter_review_obj = LetterReviewModel.objects.create(
            review_author_id=user.id, letter_id=letter_obj.id, grade=100, content="test"
        )

        letter_review_like_service(letter_review_id=letter_review_obj.id, user_id=user.id)

        target = LetterReivewLikeModel.objects.get(user_id=user.id)

        with self.assertRaises(exceptions.PermissionDenied):
            letter_review_like_delete_service(letter_review_like_id=target.id, user_id=9999)

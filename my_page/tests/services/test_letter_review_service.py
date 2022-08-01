from django.test import TestCase
from rest_framework import exceptions

from main_page.models import Letter, LetterReview, WorryCategory
from my_page.services.letter_review_service import create_letter_review, delete_letter_review, edit_letter_review
from user.models import User
from worry_board.models import WorryBoard


class TestLetterReviewService(TestCase):
    """
    레터 리뷰에 대한 서비스를 검증
    """

    def test_create_letter_review(self):
        """
        레터리뷰를 만드는 서비스함수에 대한 검증
        case : 해피
        """
        letter_author = User.objects.create(username="letter_author1", nickname="letter_author1")
        worry_board_author = User.objects.create(username="worry_author1", nickname="worry_author1")
        worry_category = WorryCategory.objects.create(cate_name="학업")
        worry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="힘들어요")
        letter = Letter.objects.create(
            letter_author=letter_author,
            worryboard=worry_board,
            title="title",
            content="content",
        )
        review_data = {"grade": 5, "content": "감사합니다."}
        create_letter_review(user=worry_board_author, letter_id=letter.id, review_data=review_data)
        letter_review = LetterReview.objects.filter(letter=letter).get()
        self.assertEqual("감사합니다.", letter_review.content)
        self.assertEqual(5, letter_review.grade)
        self.assertEqual(worry_board_author, letter_review.review_author)

    def test_when_letter_does_not_exist_in_create_letter_review(self):
        """
        레터리뷰를 만드는 서비스함수에 대한 검증
        case : letter가 없을 경우
        """
        worry_board_author = User.objects.create(username="worry_author1", nickname="worry_author1")
        review_data = {"grade": 5, "content": "감사합니다."}
        with self.assertRaises(Letter.DoesNotExist):
            create_letter_review(user=worry_board_author, letter_id=9999, review_data=review_data)

    def test_when_invalid_data_in_create_letter_review(self):
        """
        레터리뷰를 만드는 서비스함수에 대한 검증
        case : review_data가 invalid한 경우
        """
        letter_author = User.objects.create(username="letter_author1", nickname="letter_author1")
        worry_board_author = User.objects.create(username="worry_author1", nickname="worry_author1")
        worry_category = WorryCategory.objects.create(cate_name="학업")
        worry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="힘들어요")
        letter = Letter.objects.create(
            letter_author=letter_author,
            worryboard=worry_board,
            title="title",
            content="content",
        )
        review_data = {"grade": "오", "content": "감사합니다."}
        with self.assertRaises(exceptions.ValidationError):
            create_letter_review(user=worry_board_author, letter_id=letter.id, review_data=review_data)

    def test_when_invalid_user_try_to_create_letter_review(self):
        """
        레터리뷰를 만드는 서비스함수에 대한 검증
        case : 워리보드 작성자가 아닌 다른 사람이 시도하려고 할 때
        """
        letter_author = User.objects.create(username="letter_author1", nickname="letter_author1")
        worry_board_author = User.objects.create(username="worry_author1", nickname="worry_author1")
        worry_category = WorryCategory.objects.create(cate_name="학업")
        worry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="힘들어요")
        letter = Letter.objects.create(
            letter_author=letter_author,
            worryboard=worry_board,
            title="title",
            content="content",
        )
        review_data = {"grade": 5, "content": "감사합니다."}
        with self.assertRaises(PermissionError):
            create_letter_review(user=letter_author, letter_id=letter.id, review_data=review_data)

    def test_edit_letter_review(self):
        """
        레터 리뷰를 수정하는 서비스에 대한 검증
        case : 해피
        """
        letter_author = User.objects.create(username="letter_author1", nickname="letter_author1")
        worry_board_author = User.objects.create(username="worry_author1", nickname="worry_author1")
        worry_category = WorryCategory.objects.create(cate_name="학업")
        worry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="힘들어요")
        letter = Letter.objects.create(
            letter_author=letter_author,
            worryboard=worry_board,
            title="title",
            content="content",
        )
        review_data = {"grade": 5, "content": "감사합니다."}

        create_letter_review(user=worry_board_author, letter_id=letter.id, review_data=review_data)
        letter_review = LetterReview.objects.filter(letter=letter, review_author=worry_board_author).get()
        edit_data = {"grade": 3, "content": "그냥 뭐 그렇습니다."}
        edit_letter_review(user=worry_board_author, letter_review_id=letter_review.id, edit_data=edit_data)
        letter_review = LetterReview.objects.filter(letter=letter, review_author=worry_board_author).get()
        self.assertEqual(3, letter_review.grade)
        self.assertEqual("그냥 뭐 그렇습니다.", letter_review.content)

    def test_when_invalid_data_in_edit_letter_review(self):
        """
        레터 리뷰를 수정하는 서비스에 대한 검증
        case : 수정하려는 값이 invalid할 때
        """
        letter_author = User.objects.create(username="letter_author1", nickname="letter_author1")
        worry_board_author = User.objects.create(username="worry_author1", nickname="worry_author1")
        worry_category = WorryCategory.objects.create(cate_name="학업")
        worry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="힘들어요")
        letter = Letter.objects.create(
            letter_author=letter_author,
            worryboard=worry_board,
            title="title",
            content="content",
        )
        review_data = {"grade": 5, "content": "감사합니다."}

        create_letter_review(user=worry_board_author, letter_id=letter.id, review_data=review_data)
        letter_review = LetterReview.objects.filter(letter=letter, review_author=worry_board_author).get()
        edit_data = {"grade": "오", "content": "그냥 뭐 그렇습니다."}

        with self.assertRaises(exceptions.ValidationError):
            edit_letter_review(user=worry_board_author, letter_review_id=letter_review.id, edit_data=edit_data)

    def test_when_letter_review_does_not_exist_edit_letter_review(self):
        """
        레터 리뷰를 수정하는 서비스에 대한 검증
        case : 레터 리뷰가 없을 때
        """
        worry_board_author = User.objects.create(username="worry_author1", nickname="worry_author1")
        edit_data = {"grade": 3, "content": "그냥 뭐 그렇습니다."}

        with self.assertRaises(LetterReview.DoesNotExist):
            edit_letter_review(user=worry_board_author, letter_review_id=999, edit_data=edit_data)

    def test_when_other_user_try_to_edit_review_edit_letter_review(self):
        """
        레터 리뷰를 수정하는 서비스에 대한 검증
        case : 다른유저가 수정하려고 시도할 때
        """
        letter_author = User.objects.create(username="letter_author1", nickname="letter_author1")
        worry_board_author = User.objects.create(username="worry_author1", nickname="worry_author1")
        worry_category = WorryCategory.objects.create(cate_name="학업")
        worry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="힘들어요")
        letter = Letter.objects.create(
            letter_author=letter_author,
            worryboard=worry_board,
            title="title",
            content="content",
        )
        review_data = {"grade": 5, "content": "감사합니다."}

        create_letter_review(user=worry_board_author, letter_id=letter.id, review_data=review_data)
        letter_review = LetterReview.objects.filter(letter=letter, review_author=worry_board_author).get()
        edit_data = {"grade": 3, "content": "그냥 뭐 그렇습니다."}
        with self.assertRaises(PermissionError):
            edit_letter_review(user=letter_author, letter_review_id=letter_review.id, edit_data=edit_data)

    def test_delete_letter_review(self):
        """
        레터 리뷰를 삭제하는 서비스에 대한 검증
        case : 해피
        """
        letter_author = User.objects.create(username="letter_author1", nickname="letter_author1")
        worry_board_author = User.objects.create(username="worry_author1", nickname="worry_author1")
        worry_category = WorryCategory.objects.create(cate_name="학업")
        worry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="힘들어요")
        letter = Letter.objects.create(
            letter_author=letter_author,
            worryboard=worry_board,
            title="title",
            content="content",
        )
        review_data = {"grade": 5, "content": "감사합니다."}
        create_letter_review(user=worry_board_author, letter_id=letter.id, review_data=review_data)

        letter_review = LetterReview.objects.filter(review_author=worry_board_author, letter=letter).get()

        delete_letter_review(user=worry_board_author, letter_review_id=letter_review.id)

        with self.assertRaises(LetterReview.DoesNotExist):
            letter_review = LetterReview.objects.filter(review_author=worry_board_author, letter=letter).get()

    def test_when_letter_review_model_does_not_exist_delete_letter_review(self):
        """
        레터 리뷰를 삭제하는 서비스에 대한 검증
        case : 레터리뷰모델이 없을 때
        """
        letter_author = User.objects.create(username="letter_author1", nickname="letter_author1")
        worry_board_author = User.objects.create(username="worry_author1", nickname="worry_author1")
        worry_category = WorryCategory.objects.create(cate_name="학업")
        worry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="힘들어요")
        Letter.objects.create(
            letter_author=letter_author,
            worryboard=worry_board,
            title="title",
            content="content",
        )
        with self.assertRaises(LetterReview.DoesNotExist):
            delete_letter_review(user=worry_board_author, letter_review_id=999)

    def test_when_invalid_user_try_to_delete_letter_review(self):
        """
        레터 리뷰를 삭제하는 서비스에 대한 검증
        case : 다른 유저가 삭제를 시도할 때
        """
        letter_author = User.objects.create(username="letter_author1", nickname="letter_author1")
        worry_board_author = User.objects.create(username="worry_author1", nickname="worry_author1")
        worry_category = WorryCategory.objects.create(cate_name="학업")
        worry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="힘들어요")
        letter = Letter.objects.create(
            letter_author=letter_author,
            worryboard=worry_board,
            title="title",
            content="content",
        )
        review_data = {"grade": 5, "content": "감사합니다."}
        create_letter_review(user=worry_board_author, letter_id=letter.id, review_data=review_data)

        letter_review = LetterReview.objects.filter(review_author=worry_board_author, letter=letter).get()

        with self.assertRaises(PermissionError):
            delete_letter_review(user=letter_author, letter_review_id=letter_review.id)

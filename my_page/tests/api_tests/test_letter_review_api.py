import json

from rest_framework.test import APIClient, APITestCase

from main_page.models import Letter as LetterModel
from main_page.models import LetterReview as LetterReviewModel
from main_page.models import WorryCategory as WorryCategoryModel
from main_page.services.letter_service import letter_post_service
from user.models import MongleGrade as MongleGradeModel
from user.models import MongleLevel as MongleLevelModel
from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel
from worry_board.models import WorryBoard as WorryBoardModel


class TestLetterReviewView(APITestCase):
    """
    LetterReviewView를 검증하는 클래스
    """

    @classmethod
    def setUpTestData(cls):
        letter_author = UserModel.objects.create(username="letter_author", nickname="letter_author")
        UserProfileModel.objects.create(user=letter_author)
        mongle_level = MongleLevelModel.objects.create(id=1)
        MongleGradeModel.objects.create(user=letter_author, mongle_level=mongle_level)

        worry_author = UserModel.objects.create(username="worry_author", nickname="worry_author")
        UserProfileModel.objects.create(user=worry_author)
        MongleGradeModel.objects.create(user=worry_author, mongle_level=mongle_level)

        category = WorryCategoryModel.objects.create(cate_name="1")

        worry_board = WorryBoardModel.objects.create(author=worry_author, category=category)

        letter_post_service(
            letter_author=letter_author,
            request_data={"title": "title", "content": "content", "worry_board_id": worry_board.id},
        )
        letter_author.refresh_from_db()
        worry_author.refresh_from_db()

    def test_post_letter_review(self) -> None:
        """
        LetterReviewView의 post 함수를 검증
        case : 해피
        """
        client = APIClient()
        letter_author = UserModel.objects.filter(username="letter_author").get()
        worry_author = UserModel.objects.filter(username="worry_author").get()
        letter = LetterModel.objects.get(letter_author=letter_author)

        client.force_authenticate(user=worry_author)
        url = "/my_page/letter_review?letter_id=" + str(letter.id)
        response = client.post(url, json.dumps({"grade": 5, "content": "사랑해요"}), content_type="application/json")
        result = response.json()

        self.assertEqual(201, response.status_code)
        self.assertEqual("햇살 님에게 몽글점수를 50점 주셨습니다!", result["detail"])

    def test_when_invalid_data_is_given_post_letter_review(self) -> None:
        """
        LetterReviewView의 post 함수를 검증
        case : invalid_data
        """

        client = APIClient()
        letter_author = UserModel.objects.filter(username="letter_author").get()
        worry_author = UserModel.objects.filter(username="worry_author").get()
        letter = LetterModel.objects.get(letter_author=letter_author)

        client.force_authenticate(user=worry_author)
        url = "/my_page/letter_review?letter_id=" + str(letter.id)
        response = client.post(url, json.dumps({"grade": "dh", "content": "사랑해요"}), content_type="application/json")
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual("리뷰 생성에 실패했습니다. 리뷰를 다시 한번 확인하신 후에 시도해주세요.", result["detail"])

    def test_when_query_param_is_empty_post_letter_review(self) -> None:
        """
        LetterReviewView의 post 함수를 검증
        case : 빈 쿼리 파라미터를 보낼 때
        """

        client = APIClient()
        worry_author = UserModel.objects.filter(username="worry_author").get()

        client.force_authenticate(user=worry_author)
        url = "/my_page/letter_review"
        response = client.post(url, json.dumps({"grade": "dh", "content": "사랑해요"}), content_type="application/json")
        result = response.json()

        self.assertEqual(404, response.status_code)
        self.assertEqual("편지를 찾을 수가 없습니다.", result["detail"])

    def test_when_letter_does_not_exist_post_letter_review(self) -> None:
        """
        LetterReviewView의 post 함수를 검증
        case : 편지가 없을 때
        """

        client = APIClient()
        worry_author = UserModel.objects.filter(username="worry_author").get()

        client.force_authenticate(user=worry_author)
        url = "/my_page/letter_review?letter_id=" + str(999)
        response = client.post(url, json.dumps({"grade": "dh", "content": "사랑해요"}), content_type="application/json")
        result = response.json()

        self.assertEqual(404, response.status_code)
        self.assertEqual("편지를 찾을 수가 없습니다.", result["detail"])

    def test_when_invalid_user_try_to_post_letter_review(self) -> None:
        """
        LetterReviewView의 post 함수를 검증
        case : 워리보드 작성자가 아닌 사람이 리뷰를 달려고 할 때
        """

        client = APIClient()
        letter_author = UserModel.objects.filter(username="letter_author").get()
        letter = LetterModel.objects.get(letter_author=letter_author)

        client.force_authenticate(user=letter_author)
        url = "/my_page/letter_review?letter_id=" + str(letter.id)
        response = client.post(url, json.dumps({"grade": 5, "content": "사랑해요"}), content_type="application/json")
        result = response.json()

        self.assertEqual(203, response.status_code)
        self.assertEqual("생성 권한이 없습니다.", result["detail"])

    def test_put_letter_review(self) -> None:
        """
        LetterReviewView의 put 함수를 검증
        case : 해피
        """

        client = APIClient()
        worry_author = UserModel.objects.filter(username="worry_author").get()
        letter = LetterModel.objects.get(worryboard__author=worry_author)
        letter_review_before = LetterReviewModel.objects.create(
            review_author=worry_author, letter=letter, grade=3, content="음 그저 그래요."
        )
        client.force_authenticate(user=worry_author)
        url = "/my_page/letter_review?letter_review_id=" + str(letter_review_before.id)
        response = client.put(url, json.dumps({"grade": 5, "content": "사랑해요"}), content_type="application/json")
        result = response.json()

        letter_review = LetterReviewModel.objects.filter(
            review_author=worry_author,
            letter=letter,
        ).get()
        self.assertEqual(200, response.status_code)
        self.assertEqual("리뷰 수정이 완료되었습니다.", result["detail"])
        self.assertEqual(5, letter_review.grade)
        self.assertEqual("사랑해요", letter_review.content)

    def test_when_invalid_user_try_to_put_letter_review(self) -> None:
        """
        LetterReviewView의 put 함수를 검증
        case : 다른 유저가 리뷰를 수정하려고 할 때
        """

        client = APIClient()
        letter_author = UserModel.objects.filter(username="letter_author").get()
        worry_author = UserModel.objects.filter(username="worry_author").get()
        letter = LetterModel.objects.get(letter_author=letter_author)
        letter_review_before = LetterReviewModel.objects.create(
            review_author=worry_author, letter=letter, grade=3, content="음 그저 그래요."
        )

        client.force_authenticate(user=letter_author)
        url = "/my_page/letter_review?letter_review_id=" + str(letter_review_before.id)
        response = client.put(url, json.dumps({"grade": 5, "content": "사랑해요"}), content_type="application/json")
        result = response.json()

        self.assertEqual(203, response.status_code)
        self.assertEqual("수정권한이 없습니다.", result["detail"])

    def test_when_invalid_data_is_given_put_letter_review(self) -> None:
        """
        LetterReviewView의 put 함수를 검증
        case : 유효하지 않은 데이터 일 때
        """

        client = APIClient()
        letter_author = UserModel.objects.filter(username="letter_author").get()
        worry_author = UserModel.objects.filter(username="worry_author").get()
        letter = LetterModel.objects.get(letter_author=letter_author)
        letter_review_before = LetterReviewModel.objects.create(
            review_author=worry_author, letter=letter, grade=3, content="음 그저 그래요."
        )

        client.force_authenticate(user=worry_author)
        url = "/my_page/letter_review?letter_review_id=" + str(letter_review_before.id)
        response = client.put(url, json.dumps({"grade": "오", "content": "사랑해요"}), content_type="application/json")
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual("리뷰 수정에 실패했습니다. 리뷰를 다시 한 번 확인하신 후에 시도해주세요.", result["detail"])

    def test_when_letter_review_does_not_exist_put_letter_review(self) -> None:
        """
        LetterReviewView의 put 함수를 검증
        case : 레터 리뷰 모델이 없을 때
        """

        client = APIClient()
        worry_author = UserModel.objects.filter(username="worry_author").get()

        client.force_authenticate(user=worry_author)
        url = "/my_page/letter_review?letter_review_id=" + str(999)
        response = client.put(url, json.dumps({"grade": "오", "content": "사랑해요"}), content_type="application/json")
        result = response.json()

        self.assertEqual(404, response.status_code)
        self.assertEqual("없는 리뷰에 접근하려고 합니다.", result["detail"])

    def test_query_parameter_empty_put_letter_review(self) -> None:
        """
        LetterReviewView의 put 함수를 검증
        case : 쿼리 파라미터가 비어있을 때
        """

        client = APIClient()
        letter_author = UserModel.objects.filter(username="letter_author").get()
        worry_author = UserModel.objects.filter(username="worry_author").get()
        letter = LetterModel.objects.get(letter_author=letter_author)
        LetterReviewModel.objects.create(review_author=worry_author, letter=letter, grade=3, content="음 그저 그래요.")

        client.force_authenticate(user=worry_author)
        url = "/my_page/letter_review"
        response = client.put(url, json.dumps({"grade": "오", "content": "사랑해요"}), content_type="application/json")
        result = response.json()

        self.assertEqual(404, response.status_code)
        self.assertEqual("없는 리뷰에 접근하려고 합니다.", result["detail"])

    def test_delete_letter_review(self) -> None:
        """
        LetterReviewView의 delete 함수를 검증
        case : 해피
        """

        client = APIClient()
        letter_author = UserModel.objects.filter(username="letter_author").get()
        worry_author = UserModel.objects.filter(username="worry_author").get()
        letter = LetterModel.objects.get(letter_author=letter_author)
        letter_review_before = LetterReviewModel.objects.create(
            review_author=worry_author, letter=letter, grade=3, content="음 그저 그래요."
        )

        client.force_authenticate(user=worry_author)
        url = "/my_page/letter_review?letter_review_id=" + str(letter_review_before.id)
        response = client.delete(url)
        result = response.json()

        with self.assertRaises(LetterReviewModel.DoesNotExist):
            LetterReviewModel.objects.filter(review_author=worry_author, letter=letter).get()
        self.assertEqual(200, response.status_code)
        self.assertEqual("리뷰 삭제가 완료되었습니다.", result["detail"])

    def test_when_invalid_user_try_to_delete_letter_review(self) -> None:
        """
        LetterReviewView의 delete 함수를 검증
        case : 다른 유저가 지우려고 할 때
        """

        client = APIClient()
        letter_author = UserModel.objects.filter(username="letter_author").get()
        worry_author = UserModel.objects.filter(username="worry_author").get()
        letter = LetterModel.objects.get(letter_author=letter_author)
        letter_review_before = LetterReviewModel.objects.create(
            review_author=worry_author, letter=letter, grade=3, content="음 그저 그래요."
        )

        client.force_authenticate(user=letter_author)
        url = "/my_page/letter_review?letter_review_id=" + str(letter_review_before.id)
        response = client.delete(url)
        result = response.json()
        letter_review = LetterReviewModel.objects.filter(review_author=worry_author, letter=letter).get()

        self.assertEqual(203, response.status_code)
        self.assertEqual("삭제 권한이 없습니다.", result["detail"])
        self.assertEqual("음 그저 그래요.", letter_review.content)
        self.assertEqual(3, letter_review.grade)

    def test_when_query_parameter_is_empty_delete_letter_review(self) -> None:
        """
        LetterReviewView의 delete 함수를 검증
        case : 쿼리 파라미터가 비어있을 때
        """

        client = APIClient()
        letter_author = UserModel.objects.filter(username="letter_author").get()
        worry_author = UserModel.objects.filter(username="worry_author").get()
        letter = LetterModel.objects.get(letter_author=letter_author)
        LetterReviewModel.objects.create(review_author=worry_author, letter=letter, grade=3, content="음 그저 그래요.")

        client.force_authenticate(user=worry_author)
        url = "/my_page/letter_review"
        response = client.delete(url)
        result = response.json()

        self.assertEqual("없는 리뷰에 접근하려고 합니다.", result["detail"])
        self.assertEqual(404, response.status_code)

    def test_when_letter_review_does_not_exist_delete_letter_review(self) -> None:
        """
        LetterReviewView의 delete 함수를 검증
        case : 레터리뷰 모델이 없을 때
        """

        client = APIClient()
        letter_author = UserModel.objects.filter(username="letter_author").get()
        worry_author = UserModel.objects.filter(username="worry_author").get()
        LetterModel.objects.get(letter_author=letter_author)

        client.force_authenticate(user=worry_author)
        url = "/my_page/letter_review?letter_review_id=" + str(999)
        response = client.delete(url)
        result = response.json()

        self.assertEqual("없는 리뷰에 접근하려고 합니다.", result["detail"])
        self.assertEqual(404, response.status_code)

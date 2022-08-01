import json

from rest_framework.test import APIClient, APITestCase

from main_page.models import Letter, LetterReview, WorryCategory
from user.models import User
from user.services.user_signup_login_service import post_user_signup_data
from worry_board.models import WorryBoard


class TestLetterReviewView(APITestCase):
    """
    LetterReviewView를 검증하는 클래스
    """

    def test_post_letter_review(self) -> None:
        """
        LetterReviewView의 post 함수를 검증
        case : 해피
        """

        client = APIClient()
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worry_board_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        letter_author = User.objects.filter(username="test_letter_author").get()
        worry_board_author = User.objects.filter(username="test_worry_board_author").get()
        worry_category = WorryCategory.objects.create(cate_name="육아")
        worrry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="content")
        letter = Letter.objects.create(
            letter_author=letter_author, worryboard=worrry_board, title="title", content="content"
        )
        client.force_authenticate(user=worry_board_author)
        url = "/my_page/letter_review?letter_id=" + str(letter.id)
        response = client.post(url, json.dumps({"grade": 5, "content": "사랑해요"}), content_type="application/json")
        result = response.json()

        self.assertEqual(201, response.status_code)
        self.assertEqual("리뷰가 생성되었습니다.", result["detail"])

    def test_when_invalid_data_is_given_post_letter_review(self) -> None:
        """
        LetterReviewView의 post 함수를 검증
        case : invalid_data
        """

        client = APIClient()
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worry_board_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        letter_author = User.objects.filter(username="test_letter_author").get()
        worry_board_author = User.objects.filter(username="test_worry_board_author").get()
        worry_category = WorryCategory.objects.create(cate_name="육아")
        worrry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="content")
        letter = Letter.objects.create(
            letter_author=letter_author, worryboard=worrry_board, title="title", content="content"
        )
        client.force_authenticate(user=worry_board_author)
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
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worry_board_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        worry_board_author = User.objects.filter(username="test_worry_board_author").get()

        client.force_authenticate(user=worry_board_author)
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
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worry_board_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        worry_board_author = User.objects.filter(username="test_worry_board_author").get()
        client.force_authenticate(user=worry_board_author)
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
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worry_board_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        letter_author = User.objects.filter(username="test_letter_author").get()
        worry_board_author = User.objects.filter(username="test_worry_board_author").get()
        worry_category = WorryCategory.objects.create(cate_name="육아")
        worrry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="content")
        letter = Letter.objects.create(
            letter_author=letter_author, worryboard=worrry_board, title="title", content="content"
        )
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
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worry_board_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        letter_author = User.objects.filter(username="test_letter_author").get()
        worry_board_author = User.objects.filter(username="test_worry_board_author").get()
        worry_category = WorryCategory.objects.create(cate_name="육아")
        worrry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="content")
        letter = Letter.objects.create(
            letter_author=letter_author, worryboard=worrry_board, title="title", content="content"
        )
        letter_review_before = LetterReview.objects.create(
            review_author=worry_board_author, letter=letter, grade=3, content="음 그저 그래요."
        )
        client.force_authenticate(user=worry_board_author)
        url = "/my_page/letter_review?letter_review_id=" + str(letter_review_before.id)
        response = client.put(url, json.dumps({"grade": 5, "content": "사랑해요"}), content_type="application/json")
        result = response.json()

        letter_review = LetterReview.objects.filter(
            review_author=worry_board_author,
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
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worry_board_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        letter_author = User.objects.filter(username="test_letter_author").get()
        worry_board_author = User.objects.filter(username="test_worry_board_author").get()
        worry_category = WorryCategory.objects.create(cate_name="육아")
        worrry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="content")
        letter = Letter.objects.create(
            letter_author=letter_author, worryboard=worrry_board, title="title", content="content"
        )
        letter_review_before = LetterReview.objects.create(
            review_author=worry_board_author, letter=letter, grade=3, content="음 그저 그래요."
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
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worry_board_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        letter_author = User.objects.filter(username="test_letter_author").get()
        worry_board_author = User.objects.filter(username="test_worry_board_author").get()
        worry_category = WorryCategory.objects.create(cate_name="육아")
        worrry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="content")
        letter = Letter.objects.create(
            letter_author=letter_author, worryboard=worrry_board, title="title", content="content"
        )
        letter_review_before = LetterReview.objects.create(
            review_author=worry_board_author, letter=letter, grade=3, content="음 그저 그래요."
        )
        client.force_authenticate(user=worry_board_author)
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
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worry_board_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        worry_board_author = User.objects.filter(username="test_worry_board_author").get()

        client.force_authenticate(user=worry_board_author)
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
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worry_board_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        worry_board_author = User.objects.filter(username="test_worry_board_author").get()

        client.force_authenticate(user=worry_board_author)
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
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worry_board_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        letter_author = User.objects.filter(username="test_letter_author").get()
        worry_board_author = User.objects.filter(username="test_worry_board_author").get()
        worry_category = WorryCategory.objects.create(cate_name="육아")
        worrry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="content")
        letter = Letter.objects.create(
            letter_author=letter_author, worryboard=worrry_board, title="title", content="content"
        )
        letter_review_before = LetterReview.objects.create(
            review_author=worry_board_author, letter=letter, grade=3, content="음 그저 그래요."
        )
        client.force_authenticate(user=worry_board_author)
        url = "/my_page/letter_review?letter_review_id=" + str(letter_review_before.id)
        response = client.delete(url)
        result = response.json()

        with self.assertRaises(LetterReview.DoesNotExist):
            LetterReview.objects.filter(review_author=worry_board_author, letter=letter).get()
        self.assertEqual(200, response.status_code)
        self.assertEqual("리뷰 삭제가 완료되었습니다.", result["detail"])

    def test_when_invalid_user_try_to_delete_letter_review(self) -> None:
        """
        LetterReviewView의 delete 함수를 검증
        case : 다른 유저가 지우려고 할 때
        """

        client = APIClient()
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worry_board_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        letter_author = User.objects.filter(username="test_letter_author").get()
        worry_board_author = User.objects.filter(username="test_worry_board_author").get()
        worry_category = WorryCategory.objects.create(cate_name="육아")
        worrry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="content")
        letter = Letter.objects.create(
            letter_author=letter_author, worryboard=worrry_board, title="title", content="content"
        )
        letter_review_before = LetterReview.objects.create(
            review_author=worry_board_author, letter=letter, grade=3, content="음 그저 그래요."
        )
        client.force_authenticate(user=letter_author)
        url = "/my_page/letter_review?letter_review_id=" + str(letter_review_before.id)
        response = client.delete(url)
        result = response.json()
        letter_review = LetterReview.objects.filter(review_author=worry_board_author, letter=letter).get()
        self.assertEqual(203, response.status_code)
        self.assertEqual("삭제 권한이 없습니다.", result["detail"])
        self.assertEqual("음 그저 그래요.", letter_review.content)
        self.assertEqual(3, letter_review.grade)

    def test_when_query_parameter_is_empty_delete_letter_review(self) -> None:
        """
        LetterReviewView의 delete 함수를 검증
        case : 다른 유저가 지우려고 할 때
        """

        client = APIClient()
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worry_board_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        letter_author = User.objects.filter(username="test_letter_author").get()
        worry_board_author = User.objects.filter(username="test_worry_board_author").get()
        worry_category = WorryCategory.objects.create(cate_name="육아")
        worrry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="content")
        letter = Letter.objects.create(
            letter_author=letter_author, worryboard=worrry_board, title="title", content="content"
        )
        LetterReview.objects.create(review_author=worry_board_author, letter=letter, grade=3, content="음 그저 그래요.")
        worry_board_author = User.objects.filter(username="test_worry_board_author").get()

        client.force_authenticate(user=worry_board_author)
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
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worry_board_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        letter_author = User.objects.filter(username="test_letter_author").get()
        worry_board_author = User.objects.filter(username="test_worry_board_author").get()
        worry_category = WorryCategory.objects.create(cate_name="육아")
        worrry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category, content="content")
        letter = Letter.objects.create(
            letter_author=letter_author, worryboard=worrry_board, title="title", content="content"
        )
        LetterReview.objects.create(review_author=worry_board_author, letter=letter, grade=3, content="음 그저 그래요.")
        client.force_authenticate(user=letter_author)
        url = "/my_page/letter_review?letter_review_id=" + str(999)
        response = client.delete(url)
        result = response.json()

        self.assertEqual("없는 리뷰에 접근하려고 합니다.", result["detail"])
        self.assertEqual(404, response.status_code)

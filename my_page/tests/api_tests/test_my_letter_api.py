from rest_framework.test import APIClient, APITestCase

from main_page.models import WorryCategory as WorryCategoryModel
from main_page.services.letter_service import letter_post_service
from user.models import User as UserModel
from user.services.user_signup_login_service import post_user_signup_data
from worry_board.models import WorryBoard


class TestMyLetter(APITestCase):
    """
    MyLetterView를 검증하는 클래스
    """

    def test_get_my_letter_view(self) -> None:
        """
        MyLetterView의 get함수를 검증
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
        worry_board_author = UserModel.objects.get(username="test_worry_board_author")
        category = WorryCategoryModel.objects.create(cate_name="1")
        worry_board = WorryBoard.objects.create(
            author=worry_board_author, category=category
        )
        letter_author = UserModel.objects.get(username="test_letter_author")
        letter_post_service(
            letter_author=letter_author,
            request_data={
                "worry_board_id": worry_board.id,
                "title": "dd",
                "content": "dd",
            },
        )

        client.force_authenticate(user=letter_author)
        url = "/my_page/my_letter?letter_num=0"
        response = client.get(url)
        result = response.json()

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, result["letter_cnt"])
        self.assertEqual("1", result["letter"]["category"])

    def test_when_letter_num_is_not_added_in_get_my_letter_view(self) -> None:
        """
        MyLetterView의 get함수를 검증
        case: 쿼리파람스에 letter_num값이 없을 때
        """
        client = APIClient()
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        user = UserModel.objects.get(username="test_letter_author")
        client.force_authenticate(user=user)
        url = "/my_page/my_letter"
        response = client.get(url)

        self.assertEqual("올바른 편지 번호를 입력해주세요.", response.json()["detail"])
        self.assertEqual(400, response.status_code)

    def test_when_letter_does_not_exist_in_get_my_letter_view(self) -> None:
        """
        MyLetterView의 get함수를 검증
        case: 없는 레터 값이 주어졌을 때
        """
        client = APIClient()
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        user = UserModel.objects.get(username="test_letter_author")
        client.force_authenticate(user=user)
        url = "/my_page/my_letter"
        response = client.get(url, {"letter_num": 1})

        self.assertEqual("편지가 없습니다. 작성하러 가볼까요?", response.json()["detail"])
        self.assertEqual(303, response.status_code)

    def test_unauthorized_user_in_get_my_letter_view(self) -> None:
        """
        MyLetterView의 get함수를 검증
        case: 인증되지 않은 유저일 때
        """
        client = APIClient()

        url = "/my_page/my_letter"
        response = client.get(url, {"letter_num": 1})

        self.assertEqual(
            "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.",
            response.json()["detail"],
        )
        self.assertEqual(401, response.status_code)


class TestMyRecievedLetterView(APITestCase):
    """
    MyRecievedLetterView를 검증하는 클래스
    """

    def test_get_my_letter_view(self) -> None:
        """
        MyRecievedLetterView의 get함수를 검증
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
        worry_board_author = UserModel.objects.get(username="test_worry_board_author")
        category = WorryCategoryModel.objects.create(cate_name="1")
        worry_board = WorryBoard.objects.create(
            author=worry_board_author, category=category
        )
        letter_author = UserModel.objects.get(username="test_letter_author")
        letter_post_service(
            letter_author=letter_author,
            request_data={
                "worry_board_id": worry_board.id,
                "title": "dd",
                "content": "dd",
            },
        )

        client.force_authenticate(user=worry_board_author)
        url = "/my_page/my_recieved_letter"
        response = client.get(url, {"letter_num": 0})
        result = response.json()

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, result["letter_cnt"])
        self.assertEqual("1", result["letter"]["category"])

    def test_when_letter_num_is_not_added_in_get_my_letter_view(self) -> None:
        """
        MyRecievedLetterView의 get함수를 검증
        case: 쿼리파람스에 letter_num값이 없을 때
        """
        client = APIClient()
        post_user_signup_data(
            user_data={
                "username": "test_user",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        user = UserModel.objects.get(username="test_user")
        client.force_authenticate(user=user)
        url = "/my_page/my_recieved_letter"
        response = client.get(url)

        self.assertEqual("올바른 편지 번호를 입력해주세요.", response.json()["detail"])
        self.assertEqual(400, response.status_code)

    def test_when_letter_does_not_exist_in_get_my_letter_view(self) -> None:
        """
        MyRecievedLetterView의 get함수를 검증
        case: 없는 레터 값이 주어졌을 때
        """
        client = APIClient()
        post_user_signup_data(
            user_data={
                "username": "test_worry_board_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        user = UserModel.objects.get(username="test_worry_board_author")
        client.force_authenticate(user=user)
        url = "/my_page/my_recieved_letter"
        response = client.get(url, {"letter_num": 0})

        self.assertEqual("편지가 없습니다. 편지를 받으러 가볼까요?", response.json()["detail"])
        self.assertEqual(303, response.status_code)

    def test_unauthorized_user_in_get_my_letter_view(self) -> None:
        """
        MyRecievedLetterView의 get함수를 검증
        case: 인증되지 않은 유저일 때
        """
        client = APIClient()

        url = "/my_page/my_recieved_letter"
        response = client.get(url, {"letter_num": 0})

        self.assertEqual(
            "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.",
            response.json()["detail"],
        )
        self.assertEqual(401, response.status_code)

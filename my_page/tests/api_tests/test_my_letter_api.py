from rest_framework.test import APIClient, APITestCase

from jin.models import Letter, WorryCategory
from user.models import User as UserModel
from worry_board.models import WorryBoard


class TestMyPage(APITestCase):
    def test_letter_num_is_not_added(self):
        client = APIClient()
        user = UserModel.objects.create(username="joo", password="1234", nickname="joo")

        client.force_authenticate(user=user)
        url = "/my_page/my_letter"
        response = client.get(url)

        self.assertEqual("올바른 편지 번호를 입력해주세요.", response.json()["detail"])
        self.assertEqual(400, response.status_code)

    def test_letter_does_not_exist(self):
        client = APIClient()
        user = UserModel.objects.create(username="joo", password="1234", nickname="joo")

        client.force_authenticate(user=user)
        url = "/my_page/my_letter"
        response = client.get(url, {"letter_num": 1})

        self.assertEqual("편지가 없습니다. 작성하러 가볼까요?", response.json()["detail"])
        self.assertEqual(404, response.status_code)

    def test_unauthorized_user(self):
        client = APIClient()

        url = "/my_page/my_letter"
        response = client.get(url, {"letter_num": 1})

        self.assertEqual(
            "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.",
            response.json()["detail"],
        )
        self.assertEqual(401, response.status_code)

    def test_get_my_letter(self):
        client = APIClient()
        letter_author = UserModel.objects.create(
            username="joo", password="1234", nickname="joo"
        )
        worry_board_author = UserModel.objects.create(
            username="woo", password="1234", nickname="woo"
        )
        category = WorryCategory.objects.create(cate_name="1")
        worry_board = WorryBoard.objects.create(
            author=worry_board_author, category=category
        )
        Letter.objects.create(
            letter_author=letter_author,
            worryboard=worry_board,
        )

        client.force_authenticate(user=letter_author)
        url = "/my_page/my_letter"
        response = client.get(url, {"letter_num": 0})

        # self.assertEqual("편지가 없습니다. 작성하러 가볼까요?", response.json()['detail'])
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.json()["letter_cnt"])
        self.assertEqual("1", response.json()["letter"]["category"])

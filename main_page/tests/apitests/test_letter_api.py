import json

from rest_framework.test import APIClient, APITestCase

from main_page.models import Letter as LetterModel
from main_page.models import WorryCategory as WorryCategoryModel
from user.models import MongleLevel
from user.models import User as UserModel
from user.services.user_signup_login_service import post_user_signup_data
from worry_board.models import WorryBoard as WorryBoardModel


class TestLetterviewAPI(APITestCase):
    """
    Letterview 의 API를 검증하는 클래스
    """

    @classmethod
    def setUpTestData(cls):
        user_data = {"username": "hajin_test", "password": "p@ssword", "nickname": "1"}
        user_data_author = {"username": "author_test", "password": "p@ssword", "nickname": "2"}
        MongleLevel.objects.create(id=1)
        post_user_signup_data(user_data)
        post_user_signup_data(user_data_author)
        daily_cate = WorryCategoryModel.objects.create(cate_name="일상")
        receive_user = UserModel.objects.get(username="hajin_test")

        WorryBoardModel.objects.create(author_id=receive_user.id, content="test", category_id=daily_cate.id)

    def test_letter_post(self) -> None:
        """
        Letterview 의 post 함수를 검증하는 함수
        """
        client = APIClient()
        receive_user = UserModel.objects.get(username="hajin_test")
        author_user = UserModel.objects.get(username="author_test")

        worry_obj = WorryBoardModel.objects.get(author=receive_user)

        client.force_authenticate(user=author_user)
        url = "/main_page/letter/"
        letter_title = "테스트 입니다!"
        letter_content = "테스트 입니다!"
        response = client.post(
            url,
            json.dumps(
                {
                    "worry_board_id": worry_obj.id,
                    "title": letter_title,
                    "content": letter_content,
                }
            ),
            content_type="application/json",
        )
        result = response.json()

        test_letter_obj = LetterModel.objects.order_by("-create_date")[:1].get().letter_author.id
        self.assertEqual(1, UserModel.objects.get(id=receive_user.id).received_letter_cnt)
        self.assertEqual(1, UserModel.objects.get(id=author_user.id).sent_letter_cnt)
        self.assertEqual(200, response.status_code)
        self.assertEqual(author_user.id, test_letter_obj)
        self.assertEqual(result["detail"], "몽글점수를 100점 획득 하셨습니다!")

    def test_inappropriate_content_letter_post(self) -> None:
        """
        Letterview 의 post 함수를 검증하는 함수
        case:  부적절한 내용이 담겨있을 때
        """
        client = APIClient()
        user = UserModel.objects.get(username="author_test")
        receive_user = UserModel.objects.get(username="hajin_test")

        worry_obj = WorryBoardModel.objects.get(author=receive_user)

        client.force_authenticate(user=user)
        url = "/main_page/letter/"
        letter_title = "테스트 입니다!"
        letter_content = "시발시발시발시발"
        response = client.post(
            url,
            json.dumps(
                {
                    "worry_board_id": worry_obj.id,
                    "title": letter_title,
                    "content": letter_content,
                }
            ),
            content_type="application/json",
        )
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual(result["detail"], "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다")

    def test_overlap_letter_post(self) -> None:
        """
        Letterview 의 post 함수를 검증하는 함수
        case: 이미 편지를 작성했을 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="author_test")
        receive_user = UserModel.objects.get(username="hajin_test")

        worry_obj = WorryBoardModel.objects.get(author=receive_user)
        LetterModel.objects.create(
            letter_author_id=user.id,
            worryboard_id=worry_obj.id,
            title="test",
            content="content",
        )

        client.force_authenticate(user=user)
        url = "/main_page/letter/"
        letter_title = "테스트 입니다!"
        letter_content = "테스트 입니다!"
        response = client.post(
            url,
            json.dumps(
                {
                    "worry_board_id": worry_obj.id,
                    "title": letter_title,
                    "content": letter_content,
                }
            ),
            content_type="application/json",
        )
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual(result["detail"], "이미 편지를 작성 하셨습니다.")

    def test_when_user_is_unauthenticated_in_letter_post(self) -> None:
        """
        Letterview 의 post 함수를 검증하는 함수
        case : 인증되지 않은 유저일 때
        """
        client = APIClient()

        url = "/main_page/letter/"
        response = client.get(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual("자격 인증데이터(authentication credentials)가 제공되지 않았습니다.", result["detail"])


class TestLetterIsReadView(APITestCase):
    """
    LetterisReadView 의 API를 검증하는 클래스
    """

    @classmethod
    def setUpTestData(cls):
        user_data = {"username": "hajin_test", "password": "p@ssword", "nickname": "1"}
        user_data_author = {"username": "author_test", "password": "p@ssword", "nickname": "2"}
        MongleLevel.objects.create(id=1)
        post_user_signup_data(user_data)
        post_user_signup_data(user_data_author)

        daily_cate = WorryCategoryModel.objects.create(cate_name="일상")
        receive_user = UserModel.objects.get(username="hajin_test")

        WorryBoardModel.objects.create(author_id=receive_user.id, content="test", category_id=daily_cate.id)

    def test_letter_is_read_post(self) -> None:
        """
        LetterReviewLike 의 post 함수를 검증하는 함수
        """
        client = APIClient()
        receive_user = UserModel.objects.get(username="hajin_test")
        author_user = UserModel.objects.get(username="author_test")

        worry_obj = WorryBoardModel.objects.get(author=receive_user)
        letter_obj = LetterModel.objects.create(
            letter_author=author_user,
            worryboard=worry_obj,
            title="테스트입니다",
            content="테스트입니다",
        )

        client.force_authenticate(user=receive_user)
        url = f"/main_page/letter/{letter_obj.id}"
        response = client.post(
            url,
        )
        self.assertEqual(0, UserModel.objects.get(id=receive_user.id).received_letter_cnt)
        self.assertEqual(200, response.status_code)

    def test_when_user_is_unauthenticated_in_letter_read_post(self) -> None:
        """
        LetterisReadView 의 post 함수를 검증하는 함수
        case : 인증되지 않은 유저일 때
        """
        client = APIClient()
        receive_user = UserModel.objects.get(username="hajin_test")
        author_user = UserModel.objects.get(username="author_test")
        worry_obj = WorryBoardModel.objects.get(author_id=receive_user.id)
        letter_obj = LetterModel.objects.create(
            letter_author=author_user,
            worryboard=worry_obj,
            title="테스트입니다",
            content="테스트입니다",
        )
        url = f"/main_page/letter/{letter_obj.id}"
        response = client.post(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual("자격 인증데이터(authentication credentials)가 제공되지 않았습니다.", result["detail"])

    def test_when_recevie_not_to_me_letter_read_post(self) -> None:
        """
        LetterisReadView 의 post 함수를 검증하는 함수
        case : 자신이 받은 편지가 아닐 때
        """
        client = APIClient()
        receive_user = UserModel.objects.get(username="hajin_test")
        author_user = UserModel.objects.get(username="author_test")
        worry_obj = WorryBoardModel.objects.get(author_id=receive_user.id)
        letter_obj = LetterModel.objects.create(
            letter_author=author_user,
            worryboard=worry_obj,
            title="테스트입니다",
            content="테스트입니다",
        )

        client.force_authenticate(user=author_user)
        url = f"/main_page/letter/{letter_obj.id}"
        response = client.post(url)
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual("자신이 받은 편지가 아닙니다.", result["detail"])

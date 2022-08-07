from rest_framework.test import APIClient, APITestCase

from main_page.models import Letter as LetterModel
from main_page.models import WorryCategory as WorryCategoryModel
from main_page.services.letter_service import letter_post_service
from user.models import MongleGrade as MongleGradeModel
from user.models import MongleLevel as MongleLevelModel
from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel
from worry_board.models import WorryBoard as WorryBoardModel


class TestMyLetter(APITestCase):
    """
    MyLetterView를 검증하는 클래스
    """

    @classmethod
    def setUpTestData(cls):

        letter_author = UserModel.objects.create(username="letter_author", nickname="letter_author")
        UserProfileModel.objects.create(user=letter_author)
        mongle_level = MongleLevelModel.objects.create()
        MongleGradeModel.objects.create(user=letter_author, mongle_level=mongle_level)

        worry_author = UserModel.objects.create(username="worry_author", nickname="worry_author")
        UserProfileModel.objects.create(user=worry_author)
        MongleGradeModel.objects.create(user=worry_author, mongle_level=mongle_level)

        category = WorryCategoryModel.objects.create(cate_name="1")

        worry_board_my_letter = WorryBoardModel.objects.create(author=worry_author, category=category)

        letter_post_service(
            letter_author=letter_author,
            request_data={"title": "title", "content": "content", "worry_board_id": worry_board_my_letter.id},
        )
        letter_author.refresh_from_db()
        worry_author.refresh_from_db()

    def test_get_my_letter_view(self) -> None:
        """
        MyLetterView의 get함수를 검증
        """
        client = APIClient()

        letter_author = UserModel.objects.get(username="letter_author")

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

        user = UserModel.objects.get(username="letter_author")
        client.force_authenticate(user=user)
        url = "/my_page/my_letter"
        response = client.get(url)

        self.assertEqual("올바른 편지 번호를 입력해주세요.", response.json()["detail"])
        self.assertEqual(404, response.status_code)

    def test_when_letter_does_not_exist_in_get_my_letter_view(self) -> None:
        """
        MyLetterView의 get함수를 검증
        case: 없는 레터 값이 주어졌을 때
        """
        client = APIClient()

        user = UserModel.objects.get(username="letter_author")
        client.force_authenticate(user=user)
        url = "/my_page/my_letter"
        response = client.get(url, {"letter_num": 999})

        self.assertEqual("999번째 편지를 찾을 수 없습니다.", response.json()["detail"])
        self.assertEqual(404, response.status_code)

    def test_unauthorized_user_in_get_my_letter_view(self) -> None:
        """
        MyLetterView의 get함수를 검증
        case: 인증되지 않은 유저일 때
        """
        client = APIClient()

        url = "/my_page/my_letter"
        response = client.get(url, {"letter_num": 0})

        self.assertEqual(
            "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.",
            response.json()["detail"],
        )
        self.assertEqual(401, response.status_code)

    def test_when_my_profile_does_not_exist_in_get_my_letter_view(self) -> None:
        """
        MyLetterView의 get함수를 검증
        case: 내 유저 프로필이 없을 때
        """
        client = APIClient()

        letter_author = UserModel.objects.get(username="letter_author")
        UserProfileModel.objects.filter(user=letter_author).delete()

        client.force_authenticate(user=letter_author)
        url = "/my_page/my_letter?letter_num=0"
        response = client.get(url)
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual("잘못된 요청입니다. 다시 시도해주세요.", result["detail"])

    def test_when_others_profile_does_not_exist_in_get_my_letter_view(self) -> None:
        """
        MyLetterView의 get함수를 검증
        case: 상대방 유저 프로필이 없을 때
        """
        client = APIClient()
        worry_author = UserModel.objects.get(username="worry_author")
        letter_author = UserModel.objects.get(username="letter_author")

        UserProfileModel.objects.filter(user=worry_author).delete()

        client.force_authenticate(user=letter_author)
        url = "/my_page/my_letter?letter_num=0"
        response = client.get(url)
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual("잘못된 요청입니다. 다시 시도해주세요.", result["detail"])

    def test_when_others_mongle_grade_does_not_exist_in_get_my_letter_view(self) -> None:
        """
        MyLetterView의 get함수를 검증
        case: 상대방 몽글정보가 없을 때
        """
        client = APIClient()
        worry_author = UserModel.objects.get(username="worry_author")
        letter_author = UserModel.objects.get(username="letter_author")

        MongleGradeModel.objects.filter(user=worry_author).delete()

        client.force_authenticate(user=letter_author)
        url = "/my_page/my_letter?letter_num=0"
        response = client.get(url)
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual("잘못된 요청입니다. 다시 시도해주세요.", result["detail"])

    def test_when_my_mongle_grade_does_not_exist_in_get_my_letter_view(self) -> None:
        """
        MyLetterView의 get함수를 검증
        case: 내 몽글정보가 없을 때
        """
        client = APIClient()
        letter_author = UserModel.objects.get(username="letter_author")
        MongleGradeModel.objects.filter(user=letter_author).delete()

        client.force_authenticate(user=letter_author)
        url = "/my_page/my_letter?letter_num=0"
        response = client.get(url)
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual("잘못된 요청입니다. 다시 시도해주세요.", result["detail"])


class TestMyReceivedLetterView(APITestCase):
    """
    MyReceivedLetterView를 검증하는 클래스
    """

    @classmethod
    def setUpTestData(cls):

        letter_author = UserModel.objects.create(username="letter_author", nickname="letter_author")
        UserProfileModel.objects.create(user=letter_author)
        mongle_level = MongleLevelModel.objects.create()
        MongleGradeModel.objects.create(user=letter_author, mongle_level=mongle_level)

        worry_author = UserModel.objects.create(username="worry_author", nickname="worry_author")
        UserProfileModel.objects.create(user=worry_author)
        MongleGradeModel.objects.create(user=worry_author, mongle_level=mongle_level)

        category = WorryCategoryModel.objects.create(cate_name="1")

        worry_board_receive = WorryBoardModel.objects.create(author=worry_author, category=category)

        letter_post_service(
            letter_author=letter_author,
            request_data={"title": "title", "content": "content", "worry_board_id": worry_board_receive.id},
        )
        letter = LetterModel.objects.get(worryboard__author=worry_author)
        letter.is_read = True
        letter.save()
        letter_author.refresh_from_db()
        worry_author.refresh_from_db()

    def test_get_my_received_letter_view(self) -> None:
        """
        MyReceivedLetterView의 get함수를 검증
        """
        client = APIClient()

        worry_author = UserModel.objects.get(username="worry_author")

        client.force_authenticate(user=worry_author)
        url = "/my_page/my_received_letter"
        response = client.get(url, {"letter_num": 0})
        result = response.json()

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, result["letter_cnt"])
        self.assertEqual("1", result["letter"]["category"])

    def test_when_all_letters_are_not_read_get_my_received_letter_view(self) -> None:
        """
        MyReceivedLetterView의 get함수를 검증
        case: 모든 편지가 읽지않은 편지 일 때
        """
        client = APIClient()

        worry_author = UserModel.objects.get(username="worry_author")
        letter = LetterModel.objects.get(worryboard__author=worry_author)
        letter.is_read = False
        letter.save()

        client.force_authenticate(user=worry_author)
        url = "/my_page/my_received_letter"
        response = client.get(url, {"letter_num": 0})
        result = response.json()

        self.assertEqual(202, response.status_code)
        # 유저데이터만 넘기는지 검사
        self.assertEqual("worry_author", result["nickname"])

    def test_when_letter_num_is_not_added_in_get_my_received_letter_view(self) -> None:
        """
        MyReceivedLetterView의 get함수를 검증
        case: 쿼리파람스에 letter_num값이 없을 때
        """
        client = APIClient()

        user = UserModel.objects.get(username="letter_author")
        client.force_authenticate(user=user)
        url = "/my_page/my_received_letter"
        response = client.get(url)

        self.assertEqual("올바른 편지 번호를 입력해주세요.", response.json()["detail"])
        self.assertEqual(404, response.status_code)

    def test_when_letter_does_not_exist_in_get_my_recieved_letter_view(self) -> None:
        """
        MyRecievedLetterView의 get함수를 검증
        case: 편지가 없을 때
        """
        client = APIClient()

        letter_author = UserModel.objects.get(username="letter_author")
        client.force_authenticate(user=letter_author)
        url = "/my_page/my_received_letter"
        response = client.get(url, {"letter_num": 0})

        self.assertEqual("편지가 없습니다. 편지를 받으러 가볼까요?", response.json()["detail"])
        self.assertEqual(303, response.status_code)

    def test_unauthorized_user_in_get_my_recieved_letter_view(self) -> None:
        """
        MyReceivedLetterView의 get함수를 검증
        case: 인증되지 않은 유저일 때
        """
        client = APIClient()

        url = "/my_page/my_received_letter"
        response = client.get(url, {"letter_num": 0})

        self.assertEqual(
            "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.",
            response.json()["detail"],
        )
        self.assertEqual(401, response.status_code)


class TestMyNotReadLetterView(APITestCase):
    """
    MyNotReadLetterView를 검증하는 class
    """

    @classmethod
    def setUpTestData(cls):

        letter_author = UserModel.objects.create(username="letter_author", nickname="letter_author")
        UserProfileModel.objects.create(user=letter_author)
        mongle_level = MongleLevelModel.objects.create()
        MongleGradeModel.objects.create(user=letter_author, mongle_level=mongle_level)

        worry_author = UserModel.objects.create(username="worry_author", nickname="worry_author")
        UserProfileModel.objects.create(user=worry_author)
        MongleGradeModel.objects.create(user=worry_author, mongle_level=mongle_level)

        category = WorryCategoryModel.objects.create(cate_name="1")

        worry_board_not_read = WorryBoardModel.objects.create(author=worry_author, category=category)

        letter_post_service(
            letter_author=letter_author,
            request_data={"title": "title", "content": "content", "worry_board_id": worry_board_not_read.id},
        )
        letter_author.refresh_from_db()
        worry_author.refresh_from_db()

    def test_get_my_not_read_letter_view(self):
        """
        MyNotReadLetterView의 get함수를 검증
        """
        client = APIClient()

        worry_author = UserModel.objects.get(username="worry_author")

        client.force_authenticate(user=worry_author)
        url = "/my_page/my_not_read_letter"
        response = client.get(url, {"letter_num": 0})
        result = response.json()

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, result["letter_cnt"])
        self.assertEqual("1", result["letter"]["category"])

    def test_when_all_letter_is_read_get_my_not_read_letter_view(self):
        """
        MyNotReadLetterView의 get함수를 검증
        case: 편지가 모두 읽은 편지일 때
        """
        client = APIClient()

        worry_author = UserModel.objects.get(username="worry_author")
        letter = LetterModel.objects.get(worryboard__author=worry_author)
        letter.is_read = True
        letter.save()

        client.force_authenticate(user=worry_author)
        url = "/my_page/my_not_read_letter"
        response = client.get(url, {"letter_num": 0})

        self.assertEqual(303, response.status_code)

    def test_empty_params_my_not_read_letter_view(self):
        """
        MyNotReadLetterView의 get함수를 검증
        case: 쿼리 파라미터가 비어있을 때
        """
        client = APIClient()

        worry_author = UserModel.objects.get(username="worry_author")

        client.force_authenticate(user=worry_author)
        url = "/my_page/my_not_read_letter"
        response = client.get(url)
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual("올바른 편지 번호를 입력해주세요.", result["detail"])

    def test_invalid_params_my_not_read_letter_view(self):
        """
        MyNotReadLetterView의 get함수를 검증
        case: 없는 편지를 조회하려고 할 때
        """
        client = APIClient()

        worry_author = UserModel.objects.get(username="worry_author")

        client.force_authenticate(user=worry_author)
        url = "/my_page/my_not_read_letter"
        response = client.get(url, {"letter_num": 9999})
        result = response.json()

        self.assertEqual(404, response.status_code)
        self.assertEqual("9999번째 편지를 찾을 수 없습니다.", result["detail"])

    def test_when_userprofile_does_not_exist_my_not_read_letter_view(self):
        """
        MyNotReadLetterView의 get함수를 검증
        case: 유저프로필이 없을 때
        """
        client = APIClient()
        worry_author = UserModel.objects.get(username="worry_author")
        UserProfileModel.objects.filter(user=worry_author).delete()

        client.force_authenticate(user=worry_author)
        url = "/my_page/my_not_read_letter"
        response = client.get(url, {"letter_num": 0})
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual("잘못된 요청입니다. 다시 시도해주세요.", result["detail"])

    def test_when_mongle_grade_does_not_exist_my_not_read_letter_view(self):
        """
        MyNotReadLetterView의 get함수를 검증
        case: 몽글그레이드가 없을 때
        """
        client = APIClient()

        worry_author = UserModel.objects.get(username="worry_author")

        MongleGradeModel.objects.filter(user=worry_author).delete()

        client.force_authenticate(user=worry_author)
        url = "/my_page/my_not_read_letter"
        response = client.get(url, {"letter_num": 0})
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual("잘못된 요청입니다. 다시 시도해주세요.", result["detail"])

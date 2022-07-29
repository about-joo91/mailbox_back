from django.urls import reverse
from rest_framework.test import APITestCase

from user.models import User as UserModel


class TestUserRegistrationAPI(APITestCase):
    """
    회원가입 테스트 코드
    """
    def test_username_duplicate_check(self) -> None:
        """
        아이디가 중복일 때
        """
        url = reverse("user_view")
        UserModel.objects.create(username="won1", nickname="won")
        user_data = {"username": "won1", "password": "qwer1234%", "nickname": "won1"}
        response = self.client.post(url, user_data)
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("user의 사용자 계정은/는 이미 존재합니다.", result["detail"])

    def test_username_under_4_char_check(self) -> None:
        """
        아이디가 4자 이상이 아닌 경우
        """
        url = reverse("user_view")
        user_data = {"username": "won", "password": "qwer1234%", "nickname": "won1122"}
        response = self.client.post(url, user_data)
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("아이디는 4자 이상 입력해주세요.", result["detail"])


    def test_nickname_blank_check(self) -> None:
        """
        닉네임 입력하지 않은 경우
        """
        url = reverse("user_view")
        user_data = {"username": "won1", "password": "qwer1234%", "nickname": ""}
        response = self.client.post(url, user_data)
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드는 blank일 수 없습니다.", result["detail"])


    def test_nickname_duplicate_check(self) -> None:
        """
        닉네임 중복체크
        """
        url = reverse("user_view")
        UserModel.objects.create(username="joo", nickname="won")
        user_data = {"username": "won1", "password": "qwer1234%", "nickname": "won"}
        response = self.client.post(url, user_data)
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "중복된 닉네임이 존재합니다.")
        self.assertIn("중복된 닉네임이 존재합니다.", result["detail"])


    def test_password_under_8_char_check(self) -> None:
        """
        비밀번호 8자 이상이 아닌 경우
        """
        url = reverse("user_view")
        user_data = {"username": "won1", "password": "qwer123", "nickname": "won1122"}
        response = self.client.post(url, user_data)
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("비밀번호는 8자 이상 특수문자 포함해 입력해주세요", result["detail"])


    def test_password_including_special_char_check(self) -> None:
        """
        비밀번호에 특수문자가 포함되지 않은 경우
        """
        url = reverse("user_view")
        user_data = {"username": "won1", "password": "qwer1234", "nickname": "won1122"}
        response = self.client.post(url, user_data)
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("비밀번호는 8자 이상 특수문자 포함해 입력해주세요", result["detail"])
        
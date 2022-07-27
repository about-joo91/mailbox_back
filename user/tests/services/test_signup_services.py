# from django.db import connection
# from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import serializers
from rest_framework.test import APITestCase

from user.models import User as UserModel

# from user.services.user_signup_login_service import post_user_signup_data


class TestUserRegistrationAPI(APITestCase):
    """
    회원가입 테스트 코드
    """

    def test_username_under_4_char_check(self) -> None:
        """
        아이디가 4자 이상이 아닌 경우
        """
        url = reverse("user_view")
        user_data = {"username": "won", "password": "qwer1234%", "nickname": "won1122"}
        response = self.client.post(url, user_data)
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["non_field_errors"][0], "아이디는 4자 이상 입력!")


        # with self.assertRaises(serializers.ValidationError):
        #     UserModel.objects.create(
        #         username=user_data["username"], nickname=user_data["nickname"]
        #     )

    def test_nickname_blank_check(self) -> None:
        """
        닉네임 입력하지 않은 경우
        """
        url = reverse("user_view")
        user_data = {"username": "won1", "password": "qwer1234%", "nickname": ""}
        response = self.client.post(url, user_data)
        result = response.json()
        print(response)
        print(result)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["nickname"][0], "이 필드는 blank일 수 없습니다.")

        # with self.assertRaises(serializers.ValidationError):
        #     UserModel.objects.create(
        #         username=user_data["username"], nickname=user_data["nickname"]
        #     )

    def test_nickname_duplicate_check(self) -> None:
        """
        닉네임 중복체크
        """
        url = reverse("user_view")
        UserModel.objects.create(username="joo", nickname="won")
        user_data = {"username": "won1", "password": "qwer1234%", "nickname": "won"}
        response = self.client.post(url, user_data)

        self.assertEqual(response.status_code, 400)

        # with self.assertRaises(serializers.ValidationError):
        #     UserModel.objects.create(
        #         username=user_data["username"], nickname=user_data["nickname"]
        #     )

    def test_password_under_8_char_check(self) -> None:
        """
        비밀번호 8자 이상이 아닌 경우
        """
        url = reverse("user_view")
        user_data = {"username": "won1", "password": "qwer123", "nickname": "won1122"}
        response = self.client.post(url, user_data)

        self.assertEqual(response.status_code, 400)

        # with self.assertRaises(serializers.ValidationError):
        #     UserModel.objects.create(
        #         username=user_data["username"],
        #         nickname=user_data["nickname"],
        #         password=user_data["password"],
        #     )

    def test_password_including_special_char_check(self) -> None:
        """
        비밀번호에 특수문자가 포함되지 않은 경우
        """
        url = reverse("user_view")
        user_data = {"username": "won1", "password": "qwer1234", "nickname": "won1122"}
        response = self.client.post(url, user_data)

        self.assertEqual(response.status_code, 400)

# from django.db import connection
# from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APITestCase

from user.models import User as UserModel

# from user.services.user_signup_login_service import post_user_signup_data


class TestUserRegistrationAPI(APITestCase):
    """
    회원가입 API 테스트 코드
    """


class LoginTestCase(APITestCase):
    """
    로그인 테스트코드
    """

    def setUp(self) -> None:
        self.data = {"username": "won1234", "password": "qwer1234%"}
        self.user = UserModel.objects.create(username="won1234", nickname="won1122")
        self.user.set_password("qwer1234%")
        self.user.save()

    def test_login(self):
        response = self.client.post(reverse("token_obtain_pair"), self.data)
        print(response.data["access"])
        self.assertEqual(response.status_code, 200)
        print("dd")

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APITestCase

from user.services.user_signup_login_service import post_user_signup_data


class TestUserRegistrationAPI(APITestCase):
    def test_registration(self) -> None:
        url = reverse("user_view")
        user_data = {"username": "won", "password": "1234", "nickname": "won"}
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 200)

        with CaptureQueriesContext(connection) as ctx:
            post_user_signup_data(user_data)
            print("bb")
            print(ctx)

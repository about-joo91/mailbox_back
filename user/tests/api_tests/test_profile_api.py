from rest_framework.test import APIClient, APITestCase

from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel


class TestProfileAPI(APITestCase):
    def test_get_user_profile(self) -> None:
        client = APIClient()
        user = UserModel.objects.create(username="joo", password="1234", nickname="joo")
        user_profile = UserProfileModel.objects.create(user=user)

        client.force_authenticate(user=user)
        url = "/user/profile"
        response = client.get(url)
        result = response.json()

        self.assertEqual(result["fullname"], user_profile.fullname)
        self.assertEqual(result["user"], user_profile.user.username)
        self.assertEqual(result["description"], user_profile.description)
        self.assertEqual(result["mongle_level"], user_profile.mongle_level)
        self.assertEqual(result["mongle_grade"], user_profile.mongle_grade)
        self.assertEqual(result["profile_img"], user_profile.profile_img)

    def test_when_user_profile_is_none_in_get_user_profile(self) -> None:
        client = APIClient()
        user = UserModel.objects.create(username="joo", password="1234", nickname="joo")

        client.force_authenticate(user=user)
        url = "/user/profile"
        response = client.get(url)

        self.assertEqual("프로필이 없습니다. 프로필을 생성해주세요", response.json()["detail"])
        self.assertEqual(404, response.status_code)

from rest_framework.test import APIClient, APITestCase

from jin.models import WorryCategory
from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel


class TestProfileCategoryAPI(APITestCase):
    """
    유저 프로필 카테고리 api를 검증하는 클래스
    """

    def test_get_userprofile_category(self) -> None:
        """
        내 프로필에 저장된 카테고리를 제외한 카테고리 값을 제대로 가져오는지 검증
        """
        client = APIClient()
        user = UserModel.objects.create(username="joo", nickname="joo")
        user_profile = UserProfileModel.objects.create(user=user)
        WorryCategory.objects.create(cate_name="가족")
        WorryCategory.objects.create(cate_name="육아")
        user_profile.categories.add(1)

        client.force_authenticate(user=user)
        url = "/user/profile/category/"
        response = client.get(url)
        result = response.json()

        self.assertEqual(200, response.status_code)
        self.assertEqual("육아", result[0]["cate_name"])

    def test_when_user_profile_is_none_in_get_user_profile_category(self) -> None:
        """
        유저 프로필이 없을 때를 가정한 검증
        """
        client = APIClient()
        user = UserModel.objects.create(username="joo", nickname="joo")

        client.force_authenticate(user=user)
        url = "/user/profile/category/"
        response = client.get(url)
        result = response.json()

        self.assertEqual(404, response.status_code)
        self.assertEqual("유저프로필 데이터가 없습니다. 생성해주세요", result["detail"])

    def test_when_user_is_none_in_get_user_profile_category(self) -> None:
        """
        유저 프로필이 없을 때를 가정한 검증
        """
        client = APIClient()

        url = "/user/profile/category/"
        response = client.get(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual(
            "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.", result["detail"]
        )

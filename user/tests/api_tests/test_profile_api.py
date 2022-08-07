import json

from rest_framework.test import APIClient, APITestCase

from user.models import MongleGrade
from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel
from user.serializers import MongleGradeSerializer


class TestProfileAPI(APITestCase):
    """
    UserProfileView의 API를 검증하는 클래스
    """

    def test_get_user_profile(self) -> None:
        """
        UserProfileView 의 get 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.create(username="joo", password="1234", nickname="joo")
        user_profile = UserProfileModel.objects.create(user=user)
        mongle_grade = MongleGrade.objects.create(user=user)

        client.force_authenticate(user=user)
        url = "/user/profile"
        response = client.get(url)
        result = response.json()

        self.assertEqual(result["fullname"], user_profile.fullname)
        self.assertEqual(result["description"], user_profile.description)
        self.assertEqual(result["mongle_grade"], MongleGradeSerializer(mongle_grade).data)
        self.assertEqual(result["profile_img"], user_profile.profile_img)

    def test_when_user_profile_is_none_in_get_user_profile(self) -> None:
        """
        UserProfileView 의 get 함수를 검증하는 함수
        case : 유저프로필이 없을 때
        """
        client = APIClient()
        user = UserModel.objects.create(username="joo", password="1234", nickname="joo")

        client.force_authenticate(user=user)
        url = "/user/profile"
        response = client.get(url)
        result = response.json()

        self.assertEqual("잘못된 접근입니다. 다시 시도해주세요.", result["detail"])
        self.assertEqual(400, response.status_code)

    def test_when_user_is_unauthenticated_in_get_user_profile(self) -> None:
        """
        UserProfileView 의 get 함수를 검증하는 함수
        case : 인증되지 않은 유저일 때
        """
        client = APIClient()

        url = "/user/profile"
        response = client.get(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual("자격 인증데이터(authentication credentials)가 제공되지 않았습니다.", result["detail"])

    def test_put_user_profile(self) -> None:
        """
        UserProfileView 의 put 함수를 검증하는 함수
        """

        client = APIClient()
        user = UserModel.objects.create(username="joo", password="1234", nickname="joo")
        UserProfileModel.objects.create(user=user)

        client.force_authenticate(user=user)
        url = "/user/profile"
        response = client.put(
            url,
            json.dumps(
                {
                    "fullname": "방가워",
                    "description": "desc",
                }
            ),
            content_type="application/json",
        )
        result = response.json()

        userprofile = UserProfileModel.objects.filter(user=user).get()

        self.assertEqual("프로필이 수정되었습니다", result["detail"])
        self.assertEqual(200, response.status_code)
        self.assertEqual("방가워", userprofile.fullname)
        self.assertEqual("desc", userprofile.description)

    def test_when_user_profile_is_none_in_put_user_profile(self) -> None:
        """
        UserProfileView 의 put 함수를 검증하는 함수
        case : 유저프로필이 없을 때
        """
        client = APIClient()
        user = UserModel.objects.create(username="joo", password="1234", nickname="joo")

        client.force_authenticate(user=user)
        url = "/user/profile"
        response = client.put(
            url,
            json.dumps(
                {
                    "fullname": "방가워",
                    "description": "desc",
                }
            ),
            content_type="application/json",
        )
        result = response.json()

        self.assertEqual("잘못된 접근입니다. 다시 시도해주세요.", result["detail"])
        self.assertEqual(400, response.status_code)

    def test_invalid_data_in_put_user_profile(self) -> None:
        """
        UserProfileView 의 put 함수를 검증하는 함수
        case : 데이터가 유효하지 않을 때
        """
        client = APIClient()
        user = UserModel.objects.create(username="joo", password="1234", nickname="joo")
        UserProfileModel.objects.create(user=user)

        client.force_authenticate(user=user)
        url = "/user/profile"
        response = client.put(
            url,
            json.dumps(
                {
                    "profile_img": 1234431,
                }
            ),
            content_type="application/json",
        )
        result = response.json()

        self.assertEqual("프로필 수정에 실패했습니다. 정확한 값을 입력해주세요.", result["detail"])
        self.assertEqual(400, response.status_code)

    def test_when_user_is_unauthenticated_in_put_user_profile(self) -> None:
        """
        UserProfileView 의 put 함수를 검증하는 함수
        case : 인증되지 않은 유저일 때
        """
        client = APIClient()

        url = "/user/profile"
        response = client.get(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual("자격 인증데이터(authentication credentials)가 제공되지 않았습니다.", result["detail"])

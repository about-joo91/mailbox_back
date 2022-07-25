from django.test import TestCase
from rest_framework.exceptions import ValidationError

from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel
from user.services.user_profile_service import (
    get_user_profile_data,
    update_user_profile_data,
)


class TestUserProfileServices(TestCase):
    """
    유저 프로필 서비스 함수들을 검증하는 클래스
    """

    def test_when_seccess_get_profile_data(self) -> None:
        """
        프로필을 가져오는 함수에 대한 검증
        """
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)
        with self.assertNumQueries(3):
            user_profile_data = get_user_profile_data(user.id)

        self.assertEqual(0, user_profile_data["mongle_level"])
        self.assertEqual(0, user_profile_data["mongle_level"])
        self.assertEqual(
            "https://user-images.githubusercontent.com/55477835/178631292-f381c6e2-2541-4a2c-ba67-b5bb4369e3d0.jpeg",
            user_profile_data["profile_img"],
        )

    def test_when_user_profile_is_None_in_get_profile_data(self):
        """
        프로필을 가져오는 함수에 대한 검증
        case: user_profile이 none일 때
        """
        user = UserModel.objects.create(username="joo", nickname="joo")
        with self.assertRaises(UserProfileModel.DoesNotExist):
            get_user_profile_data(user_id=user.id)

    def test_when_seccess_update_user_profile_data(self) -> None:
        """
        유저프로필을 업데이트하는 함수에 대한 검증
        """
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)

        update_data = {
            "mongle_level": 1,
            "fullname": "방가워",
            "mongle_grade": 1,
            "description": "desc",
        }
        update_user_profile_data(user_id=user.id, update_data=update_data)

        userprofile = UserProfileModel.objects.filter(user=user).get()

        self.assertEqual(1, userprofile.mongle_level)
        self.assertEqual("방가워", userprofile.fullname)
        self.assertEqual("desc", userprofile.description)
        self.assertEqual(1, userprofile.mongle_grade)

    def test_when_user_profile_is_None_in_update_user_profile_data(self):
        """
        유저프로필을 업데이트하는 함수에 대한 검증
        case: 유저프로필이 none일 때
        """
        user = UserModel.objects.create(username="joo", nickname="joo")

        update_data = {
            "mongle_level": 1,
            "fullname": "방가워",
            "mongle_grade": 1,
            "description": "desc",
        }
        with self.assertRaises(UserProfileModel.DoesNotExist):
            update_user_profile_data(user_id=user.id, update_data=update_data)

    def test_when_validate_error_in_update_user_profile_data(self):
        """
        유저프로필을 업데이트하는 함수에 대한 검증
        case : serializer 밸리데이션을 통과하지 못할 때
        """
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)

        update_data = {
            "mongle_level": "test",
        }
        with self.assertRaises(ValidationError):
            update_user_profile_data(user_id=user.id, update_data=update_data)

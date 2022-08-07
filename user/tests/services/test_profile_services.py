from django.test import TestCase
from rest_framework.exceptions import ValidationError

from user.models import MongleGrade as MongleGradeModel
from user.models import MongleLevel as MongleLevelModel
from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel
from user.services.user_profile_service import get_user_profile_data, update_user_profile_data


class TestUserProfileServices(TestCase):
    """
    유저 프로필 서비스 함수들을 검증하는 클래스
    """

    @classmethod
    def setUpTestData(cls):
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)
        mongle_level = MongleLevelModel.objects.create()
        MongleGradeModel.objects.create(user=user, mongle_level=mongle_level)

        no_profile = UserModel.objects.create(username="no_profile", nickname="no_profile")
        MongleGradeModel.objects.create(user=no_profile, mongle_level=mongle_level)

        no_mongle_user = UserModel.objects.create(username="no_mongle", nickname="no_mongle")
        UserProfileModel.objects.create(user=no_mongle_user)

    def test_when_seccess_get_profile_data(self) -> None:
        """
        프로필을 가져오는 함수에 대한 검증
        """
        user = UserModel.objects.get(username="joo")

        with self.assertNumQueries(3):
            user_profile_data = get_user_profile_data(user.id)

        self.assertEqual("", user_profile_data["fullname"])
        self.assertEqual("", user_profile_data["description"])
        self.assertEqual(
            "https://user-images.githubusercontent.com/55477835/183034958-de0d010a-a105-459b-9d7b-915c04a882c7.png",
            user_profile_data["profile_img"],
        )

    def test_when_user_profile_is_None_in_get_profile_data(self):
        """
        프로필을 가져오는 함수에 대한 검증
        case: user_profile이 none일 때
        """
        user = UserModel.objects.get(username="no_profile")
        with self.assertRaises(UserProfileModel.DoesNotExist):
            get_user_profile_data(user_id=user.id)

    def test_when_monglegrade_is_None_in_get_profile_data(self):
        """
        프로필을 가져오는 함수에 대한 검증
        case: monglegrade가 none일 때
        """
        user = UserModel.objects.get(username="no_mongle")
        with self.assertRaises(MongleGradeModel.DoesNotExist):
            get_user_profile_data(user_id=user.id)

    def test_when_seccess_update_user_profile_data(self) -> None:
        """
        유저프로필을 업데이트하는 함수에 대한 검증
        """
        user = UserModel.objects.get(username="joo")

        update_data = {
            "fullname": "방가워",
            "description": "desc",
        }
        update_user_profile_data(user_id=user.id, update_data=update_data)

        userprofile = UserProfileModel.objects.filter(user=user).get()

        self.assertEqual("방가워", userprofile.fullname)
        self.assertEqual("desc", userprofile.description)

    def test_when_user_profile_is_None_in_update_user_profile_data(self):
        """
        유저프로필을 업데이트하는 함수에 대한 검증
        case: 유저프로필이 none일 때
        """
        user = UserModel.objects.get(username="no_profile")

        update_data = {
            "fullname": "방가워",
            "description": "desc",
        }
        with self.assertRaises(UserProfileModel.DoesNotExist):
            update_user_profile_data(user_id=user.id, update_data=update_data)

    def test_when_validate_error_in_update_user_profile_data(self):
        """
        유저프로필을 업데이트하는 함수에 대한 검증
        case : serializer 밸리데이션을 통과하지 못할 때
        """
        user = UserModel.objects.get(username="joo")

        update_data = {
            "profile_img": 1213,
        }
        with self.assertRaises(ValidationError):
            update_user_profile_data(user_id=user.id, update_data=update_data)

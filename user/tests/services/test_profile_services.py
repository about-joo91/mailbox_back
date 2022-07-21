from django.test import TestCase

from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel
from user.services.user_profile_service import (
    get_user_profile_data,
    update_user_profile_data,
)


class TestUserProfileServices(TestCase):
    def test_when_seccess_get_profile_data(self) -> None:
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)
        user_profile_data = get_user_profile_data(user)

        self.assertEqual("joo", user_profile_data["user"])
        self.assertEqual(0, user_profile_data["mongle_level"])
        self.assertEqual(0, user_profile_data["mongle_level"])
        self.assertEqual(
            "https://user-images.githubusercontent.com/55477835/178631292-f381c6e2-2541-4a2c-ba67-b5bb4369e3d0.jpeg",
            user_profile_data["profile_img"],
        )

    def test_when_level_up_in_profile_data(self) -> None:
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)

        update_data = {"mongle_level": 1}
        update_user_profile_data(user=user, update_data=update_data)

        self.assertEqual(1, user.userprofile.mongle_level)

    def test_when_change_name_in_profile_data(self) -> None:
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)

        update_data = {"fullname": "방가워"}
        update_user_profile_data(user=user, update_data=update_data)

        self.assertEqual("방가워", user.userprofile.fullname)

    def test_when_grade_up_in_profile_data(self) -> None:
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)

        update_data = {"mongle_grade": 1}
        update_user_profile_data(user=user, update_data=update_data)

        self.assertEqual(1, user.userprofile.mongle_grade)

    def test_when_change_desc_in_profile_data(self) -> None:
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)

        update_data = {"description": "desc"}
        update_user_profile_data(user=user, update_data=update_data)

        self.assertEqual("desc", user.userprofile.description)

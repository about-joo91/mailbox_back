from django.db import IntegrityError
from django.test import TestCase

from main_page.models import WorryCategory
from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel
from user.models import UserProfileCategory
from user.services.user_profile_category_service import (
    create_category_of_profile,
    delete_category_of_profile,
    get_category_of_profile_except_mine,
)


class TestProfileCategory(TestCase):
    """
    프로필 카테고리의 get, put 함수를 검증하는 클래스
    """

    def test_get_category_of_profile_except_mine(self) -> None:
        """
        내 프로필에 등록된 카테고리를 제외하고 모든 카테고리를 가져오는 함수를 검증
        """
        user = UserModel.objects.create(username="joo", nickname="joo")
        user_profile = UserProfileModel.objects.create(user=user)
        worry_category = WorryCategory.objects.create(cate_name="가족")
        WorryCategory.objects.create(cate_name="육아")
        WorryCategory.objects.create(cate_name="학업")

        user_profile.categories.add(worry_category)
        with self.assertNumQueries(3):
            categories = get_category_of_profile_except_mine(user.id)

        self.assertEqual("육아", categories[0]["cate_name"])
        self.assertEqual("학업", categories[1]["cate_name"])

    def test_when_userprofile_is_None_in_get_category_of_profile_except_mine(
        self,
    ) -> None:
        """
        내 프로필에 등록된 카테고리를 제외하고 모든 카테고리를 가져오는 함수를 검증
        case: 유저프로필이 없을 때
        """
        user = UserModel.objects.create(username="joo", nickname="joo")

        with self.assertRaises(UserProfileModel.DoesNotExist):
            get_category_of_profile_except_mine(user.id)

    def test_create_category_of_profile(self) -> None:
        """
        내 프로필에 카테고리를 등록하는 함수를 검증
        """
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)
        worry_category_1 = WorryCategory.objects.create(cate_name="가족")
        worry_category_2 = WorryCategory.objects.create(cate_name="육아")
        categories = [worry_category_1.id, worry_category_2.id]

        with self.assertNumQueries(3):
            create_category_of_profile(user.id, categories)

        my_categories = user.userprofile.categories.all()
        self.assertEqual(len(categories), len(my_categories))
        self.assertEqual("가족", my_categories[0].cate_name)

    def test_when_userprofile_is_None_create_category_of_profile(self) -> None:
        """
        내 프로필에 카테고리를 등록하는 함수를 검증
        case: 유저프로필이 없을 때
        """
        user = UserModel.objects.create(username="joo", nickname="joo")

        with self.assertRaises(UserProfileModel.DoesNotExist):
            create_category_of_profile(user.id, [])

    def test_when_invalid_category_is_given_to_create_category_of_profile(self) -> None:
        """
        내 프로필에 카테고리를 등록하는 함수를 검증
        case: 카테고리가 유효하지 않을 때
        """
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)
        categories = [999]

        with self.assertRaises(IntegrityError):
            create_category_of_profile(user_id=user.id, categories=categories)

    def test_delete_user_profile_category(self) -> None:
        """
        내 프로필의 카테고리를 제거하는 함수를 검증
        """
        user = UserModel.objects.create(username="joo", nickname="joo")
        user_profile = UserProfileModel.objects.create(user=user)
        worry_category = WorryCategory.objects.create(cate_name="가족")
        categories_for_create = [worry_category.id]
        create_category_of_profile(user_id=user.id, categories=categories_for_create)

        userprofile_category = UserProfileCategory.objects.filter(
            user_profile=user_profile, category=worry_category
        ).get()

        self.assertEqual(1, user.userprofile.categories.all().count())
        with self.assertNumQueries(2):
            delete_category_of_profile(user_id=user.id, p_category=userprofile_category.id)
        self.assertEqual(0, user.userprofile.categories.all().count())

    def test_when_worry_category_does_not_exist_in_delete_user_profile_category(
        self,
    ) -> None:
        """
        내 프로필의 카테고리를 제거하는 함수를 검증
        case : 프로필에 카테고리가 없을 때
        """
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)

        with self.assertRaises(UserProfileCategory.DoesNotExist):
            delete_category_of_profile(user_id=user.id, p_category=999)

    def test_shen_other_user_try_to_delete_user_profile_category(self) -> None:
        """
        내 프로필의 카테고리를 제거하는 함수를 검증
        case : 다른 유저가 지우려고 시도할 때
        """
        user = UserModel.objects.create(username="joo", nickname="joo")
        invalid_user = UserModel.objects.create(username="test", nickname="test")
        user_profile = UserProfileModel.objects.create(user=user)
        worry_category = WorryCategory.objects.create(cate_name="가족")
        categories_for_create = [worry_category.id]
        create_category_of_profile(user_id=user.id, categories=categories_for_create)

        user_profile_category = UserProfileCategory.objects.filter(
            user_profile=user_profile, category=worry_category
        ).get()

        with self.assertRaises(PermissionError):
            delete_category_of_profile(user_id=invalid_user.id, p_category=user_profile_category.id)

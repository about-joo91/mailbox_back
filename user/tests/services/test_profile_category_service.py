from django.test import TestCase

from jin.models import WorryCategory
from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel
from user.services.user_profile_category_service import (
    create_category_of_profile,
    get_category_of_profile,
)


class TestProfileCategory(TestCase):
    def test_get_profile_category(self):
        user = UserModel.objects.create(username="joo", nickname="joo")
        user_profile = UserProfileModel.objects.create(user=user)
        worry_category = WorryCategory.objects.create(cate_name="가족")
        WorryCategory.objects.create(cate_name="육아")
        WorryCategory.objects.create(cate_name="학업")

        user_profile.categories.add(worry_category)
        with self.assertNumQueries(2):
            categories = get_category_of_profile(user.id)

        self.assertEqual("육아", categories[0]["cate_name"])
        self.assertEqual("학업", categories[1]["cate_name"])

    def test_when_invalid_user_id_given_get_profile_category(self):
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)
        worry_category = WorryCategory.objects.create(cate_name="가족")
        categories = [worry_category.id]
        with self.assertNumQueries(3):
            create_category_of_profile(user.id, categories)

        my_categories = user.userprofile.categories.all()
        self.assertEqual(len(categories), len(my_categories))
        self.assertEqual("가족", my_categories[0].cate_name)

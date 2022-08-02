import json

from rest_framework.test import APIClient, APITestCase

from main_page.models import WorryCategory
from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel
from user.models import UserProfileCategory
from user.services.user_profile_category_service import create_category_of_profile


class TestProfileCategoryAPI(APITestCase):
    """
    유UserProfileCategoryViewd의 API를 검증하는 클래스
    """

    def test_get_userprofile_category(self) -> None:
        """
        UserProfileCategoryView의 get함수에 대한 검증
        """
        client = APIClient()
        user = UserModel.objects.create(username="joo", nickname="joo")
        user_profile = UserProfileModel.objects.create(user=user)
        worry_category_1 = WorryCategory.objects.create(cate_name="가족")
        WorryCategory.objects.create(cate_name="육아")
        user_profile.categories.add(worry_category_1.id)

        client.force_authenticate(user=user)
        url = "/user/profile/category/"
        response = client.get(url)
        result = response.json()

        self.assertEqual(200, response.status_code)
        self.assertEqual("육아", result[0]["cate_name"])

    def test_when_user_profile_is_none_in_get_user_profile_category(self) -> None:
        """
        UserProfileCategoryView의 get함수에 대한 검증
        case : 유저프로필이 없을 때
        """
        client = APIClient()
        user = UserModel.objects.create(username="joo", nickname="joo")

        client.force_authenticate(user=user)
        url = "/user/profile/category/"
        response = client.get(url)
        result = response.json()

        self.assertEqual(404, response.status_code)
        self.assertEqual("유저프로필 데이터가 없습니다. 생성해주세요", result["detail"])

    def test_when_user_is_unauthenticated_in_get_user_profile_category(self) -> None:
        """
        UserProfileCategoryView의 get함수에 대한 검증
        case : 인증이 되지 않은 유저일 때
        """
        client = APIClient()

        url = "/user/profile/category/"
        response = client.get(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual("자격 인증데이터(authentication credentials)가 제공되지 않았습니다.", result["detail"])

    def test_post_userprofile_category(self) -> None:
        """
        UserProfileCategoryView의 post 함수에 대한 검증
        """
        client = APIClient()
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)
        worry_category = WorryCategory.objects.create(cate_name="가족")

        client.force_authenticate(user=user)
        url = "/user/profile/category/"
        response = client.post(
            url,
            json.dumps({"categories": [worry_category.id]}),
            content_type="application/json",
        )
        result = response.json()
        categories = user.userprofile.categories.all()

        self.assertEqual("카테고리가 저장되었습니다.", result["detail"])
        self.assertEqual(200, response.status_code)
        self.assertEqual("가족", categories[0].cate_name)

    def test_when_invalid_data_is_given_to_post_userprofile_category(self) -> None:
        """
        UserProfileCategoryView의 post 함수에 대한 검증
        case : 카테고리 값이 유효하지 않을 때
        """
        client = APIClient()
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)
        WorryCategory.objects.create(cate_name="가족")

        client.force_authenticate(user=user)
        url = "/user/profile/category/"
        response = client.post(url, json.dumps({"categories": ["가족"]}), content_type="application/json")
        result = response.json()

        self.assertEqual("카테고리 생성에 실패했습니다. 정확한 값을 입력해주세요.", result["detail"])
        self.assertEqual(400, response.status_code)

    def test_when_user_profile_is_none_in_post_user_profile_category(self) -> None:
        """
        UserProfileCategoryView의 post 함수에 대한 검증
        case : 유저프로필이 없을 때
        """
        client = APIClient()
        user = UserModel.objects.create(username="joo", nickname="joo")
        worry_category = WorryCategory.objects.create(cate_name="가족")

        client.force_authenticate(user=user)
        url = "/user/profile/category/"
        response = client.post(
            url,
            json.dumps({"categories": [worry_category.id]}),
            content_type="application/json",
        )
        result = response.json()

        self.assertEqual(404, response.status_code)
        self.assertEqual("유저 프로필 정보가 없습니다. 생성해주세요", result["detail"])

    def test_when_user_is_unauthenticated_in_post_user_profile_category(self) -> None:
        """
        UserProfileCategoryView의 post 함수에 대한 검증
        case : 인증이 되지 않은 유저일 때
        """
        client = APIClient()
        worry_category = WorryCategory.objects.create(cate_name="가족")

        url = "/user/profile/category/"
        response = client.post(
            url,
            json.dumps({"categories": [worry_category.id]}),
            content_type="application/json",
        )
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual("자격 인증데이터(authentication credentials)가 제공되지 않았습니다.", result["detail"])

    def test_delete_userprofile_category(self) -> None:
        """
        UserProfileCategoryView의 delete 함수에 대한 검증
        """
        client = APIClient()
        user = UserModel.objects.create(username="joo", nickname="joo")
        user_profile = UserProfileModel.objects.create(user=user)
        worry_category = WorryCategory.objects.create(cate_name="가족")
        create_category_of_profile(user.id, [worry_category.id])
        self.assertEqual(1, user.userprofile.categories.all().count())

        userprofile_category = UserProfileCategory.objects.filter(
            user_profile=user_profile, category=worry_category
        ).get()

        client.force_authenticate(user=user)
        url = "/user/profile/category/" + str(userprofile_category.id)
        response = client.delete(url)
        result = response.json()

        self.assertEqual("카테고리를 지웠습니다.", result["detail"])
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, user.userprofile.categories.all().count())

    def test_when_parameter_doesnot_exist_in_delete_userprofile_category(self) -> None:
        """
        UserProfileCategoryView의 delete 함수에 대한 검증
        case : delete에 url에 빈 파라미터를 보냈을 때
        """
        client = APIClient()
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)
        worry_category = WorryCategory.objects.create(cate_name="가족")
        create_category_of_profile(user.id, [worry_category.id])
        self.assertEqual(1, user.userprofile.categories.all().count())

        client.force_authenticate(user=user)
        url = "/user/profile/category/"
        response = client.delete(url)
        result = response.json()

        self.assertEqual("해당 카테고리를 조회할 수 없습니다. 다시 시도해주세요.", result["detail"])
        self.assertEqual(404, response.status_code)
        self.assertEqual(1, user.userprofile.categories.all().count())

    def test_when_category_does_not_exist_in_delete_userprofile_category(self) -> None:
        """
        UserProfileCategoryView의 delete 함수에 대한 검증
        case : 아이디 값이 유효하지 않을 때
        """
        client = APIClient()
        user = UserModel.objects.create(username="joo", nickname="joo")
        UserProfileModel.objects.create(user=user)

        client.force_authenticate(user=user)
        url = "/user/profile/category/" + str(9999)
        response = client.delete(url)
        result = response.json()

        self.assertEqual("해당 카테고리를 조회할 수 없습니다. 다시 시도해주세요.", result["detail"])
        self.assertEqual(404, response.status_code)

    def test_when_user_is_unauthenticated_in_delete_user_profile_category(self) -> None:
        """
        UserProfileCategoryView의 delete 함수에 대한 검증
        case : 인증이 되지 않은 유저일 때
        """
        client = APIClient()
        worry_category = WorryCategory.objects.create(cate_name="가족")

        url = "/user/profile/category/" + str(worry_category.id)
        response = client.delete(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual("자격 인증데이터(authentication credentials)가 제공되지 않았습니다.", result["detail"])

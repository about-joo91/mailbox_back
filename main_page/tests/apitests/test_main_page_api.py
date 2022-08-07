from rest_framework.test import APIClient, APITestCase

from main_page.models import Letter as LetterModel
from main_page.models import LetterReview as LetterReviewModel
from main_page.models import WorryCategory as WorryCategoryModel
from user.models import MongleGrade as MogleGardeModel
from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel
from worry_board.models import WorryBoard as WorryBoardModel


class TestMaingPageAPI(APITestCase):
    """
    MainPageView의 API를 검증하는 클래스
    """

    def test_get_main_page(self) -> None:
        """
        MainPageView의 의 get 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.create(username="hajin", password="1234", nickname="hajin")
        UserProfileModel.objects.create(user=user)
        MogleGardeModel.objects.create(user=user, grade=100, level=1)
        category_list = ["일상", "연애", "학업", "가족", "인간관계", "육아"]
        for cate_name in category_list:
            WorryCategoryModel.objects.create(cate_name=cate_name)

        first_cate = WorryCategoryModel.objects.get(cate_name="일상").id
        last_cate = WorryCategoryModel.objects.get(cate_name="육아").id

        for woory_board_count in range(5):
            for cate_idx in range(first_cate, last_cate + 1):
                WorryBoardModel.objects.create(author_id=user.id, content="test", category_id=cate_idx)

        first_worry_obj = WorryBoardModel.objects.order_by("create_date")[:1].get().id
        last_worry_obj = WorryBoardModel.objects.order_by("-create_date")[:1].get().id

        for worry_idx in range(first_worry_obj, last_worry_obj + 1):
            LetterModel.objects.create(
                letter_author=user,
                worryboard_id=worry_idx,
                title="test",
                content="test",
            )

        first_letter_obj = LetterModel.objects.order_by("create_date")[:1].get().id
        last_letter_obj = LetterModel.objects.order_by("-create_date")[:1].get().id

        for letter_review_count in range(first_letter_obj, last_letter_obj + 1):
            LetterReviewModel.objects.create(
                review_author=user,
                letter_id=letter_review_count,
                content="test",
                grade=100,
            )

        client.force_authenticate(user=user)
        url = "/main_page/main/"
        response = client.get(url)
        result = response.json()

        self.assertEqual(200, response.status_code)
        self.assertEqual(result["letter_count"], 30)
        self.assertEqual(result["main_page_data_and_user_profile"]["user_profile_data"]["grade"], 100)
        self.assertEqual(
            result["main_page_data_and_user_profile"]["rank_list"][0]["username"],
            "hajin",
        )
        self.assertEqual(len(result["order_by_cate_worry_list"]), 18)
        self.assertEqual(len(result["best_review"]), 10)
        self.assertEqual(len(result["live_review"]), 10)

    def test_when_not_mogle_grade_is_get_main_page(self) -> None:
        """
        MainPageView의 의 get 함수를 검증하는 함수
        case: moglegrade가 없을 때
        """
        client = APIClient()
        user = UserModel.objects.create(username="hajin", password="1234", nickname="hajin")
        UserProfileModel.objects.create(user=user)
        category_list = ["일상", "연애", "학업", "가족", "인간관계", "육아"]
        for cate_name in category_list:
            WorryCategoryModel.objects.create(cate_name=cate_name)

        first_cate = WorryCategoryModel.objects.get(cate_name="일상").id
        last_cate = WorryCategoryModel.objects.get(cate_name="육아").id

        for woory_board_count in range(5):
            for cate_idx in range(first_cate, last_cate + 1):
                WorryBoardModel.objects.create(author_id=user.id, content="test", category_id=cate_idx)

        first_worry_obj = WorryBoardModel.objects.order_by("create_date")[:1].get().id
        last_worry_obj = WorryBoardModel.objects.order_by("-create_date")[:1].get().id

        for worry_idx in range(first_worry_obj, last_worry_obj + 1):
            LetterModel.objects.create(
                letter_author=user,
                worryboard_id=worry_idx,
                title="test",
                content="test",
            )

        first_letter_obj = LetterModel.objects.order_by("create_date")[:1].get().id
        last_letter_obj = LetterModel.objects.order_by("-create_date")[:1].get().id

        for letter_review_count in range(first_letter_obj, last_letter_obj + 1):
            LetterReviewModel.objects.create(
                review_author=user,
                letter_id=letter_review_count,
                content="test",
                grade=100,
            )

        client.force_authenticate(user=user)
        url = "/main_page/main/"
        response = client.get(url)
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual(result["detail"], "몽글그레이드 정보가 없습니다 생성해주세요.")

    def test_when_not_userprofile_is_get_main_page(self) -> None:
        """
        MainPageView의 의 get 함수를 검증하는 함수
        case: userprofile 데이터가 없을 때
        """
        client = APIClient()
        user = UserModel.objects.create(username="hajin", password="1234", nickname="hajin")
        MogleGardeModel.objects.create(user=user, grade=100, level=1)
        category_list = ["일상", "연애", "학업", "가족", "인간관계", "육아"]
        for cate_name in category_list:
            WorryCategoryModel.objects.create(cate_name=cate_name)

        first_cate = WorryCategoryModel.objects.get(cate_name="일상").id
        last_cate = WorryCategoryModel.objects.get(cate_name="육아").id

        for woory_board_count in range(5):
            for cate_idx in range(first_cate, last_cate + 1):
                WorryBoardModel.objects.create(author_id=user.id, content="test", category_id=cate_idx)

        first_worry_obj = WorryBoardModel.objects.order_by("create_date")[:1].get().id
        last_worry_obj = WorryBoardModel.objects.order_by("-create_date")[:1].get().id

        for worry_idx in range(first_worry_obj, last_worry_obj + 1):
            LetterModel.objects.create(
                letter_author=user,
                worryboard_id=worry_idx,
                title="test",
                content="test",
            )

        first_letter_obj = LetterModel.objects.order_by("create_date")[:1].get().id
        last_letter_obj = LetterModel.objects.order_by("-create_date")[:1].get().id

        for letter_review_count in range(first_letter_obj, last_letter_obj + 1):
            LetterReviewModel.objects.create(
                review_author=user,
                letter_id=letter_review_count,
                content="test",
                grade=100,
            )

        client.force_authenticate(user=user)
        url = "/main_page/main/"
        response = client.get(url)
        result = response.json()

        self.assertEqual(404, response.status_code)
        self.assertEqual(result["detail"], "유저프로필이 없습니다 생성해주세요.")

    def test_when_user_is_unauthenticated_in_get_main_page(self) -> None:
        """
        Mainpage 의 get 함수를 검증하는 함수
        case : 인증되지 않은 유저일 때
        """
        client = APIClient()

        url = "/main_page/main/"
        response = client.get(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual("자격 인증데이터(authentication credentials)가 제공되지 않았습니다.", result["detail"])

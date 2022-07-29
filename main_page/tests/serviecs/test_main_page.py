from django.test import TestCase

from main_page.models import Letter as LetterModel
from main_page.models import LetterReview as LetterReviewModel
from main_page.models import WorryCategory as WorryCategoryModel
from main_page.services.main_gage_service import (
    best_review_list_service,
    live_review_list_service,
    my_letter_count,
    worry_worryboard_union,
)
from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel
from worry_board.models import WorryBoard as WorryBoardModel


class TestMainPageServices(TestCase):
    def test_letter_count_service(self) -> None:
        """
        메인페이지에 도착한 읽지않은 편지 개수를 검증하는 함수를 검증
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
        test_user = UserModel.objects.create(username="test", nickname="test")
        UserProfileModel.objects.create(user=user)

        category_list = ["일상", "연애", "학업", "가족", "인간관계", "육아"]
        for cate_name in category_list:
            WorryCategoryModel.objects.create(cate_name=cate_name)

        first_cate = WorryCategoryModel.objects.get(cate_name="일상").id
        last_cate = WorryCategoryModel.objects.get(cate_name="육아").id

        worry_obj1 = WorryBoardModel.objects.create(author=user, content="ttttt", category_id=first_cate)
        worry_obj2 = WorryBoardModel.objects.create(author=user, content="ttttt", category_id=last_cate)

        letter_obj1 = LetterModel.objects.create(
            letter_author_id=test_user.id,
            worryboard_id=worry_obj1.id,
            title="test",
            content="test",
        )
        LetterModel.objects.create(
            letter_author_id=test_user.id,
            worryboard_id=worry_obj2.id,
            title="test",
            content="test",
        )

        self.assertEqual("일상", WorryCategoryModel.objects.get(id=first_cate).cate_name)
        self.assertEqual(test_user.id, LetterModel.objects.get(id=letter_obj1.id).letter_author.id)
        self.assertEqual(2, my_letter_count(user.id))

    def test_when_none_user_letter_count_service(self) -> None:
        """
        메인페이지에 도착한 읽지않은 편지 개수를 검증하는 함수를 검증
        case : user 가 유효하지 않을 때
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
        test_user = UserModel.objects.create(username="test", nickname="test")
        UserProfileModel.objects.create(user=user)

        category_list = ["일상", "연애", "학업", "가족", "인간관계", "육아"]
        for cate_name in category_list:
            WorryCategoryModel.objects.create(cate_name=cate_name)

        first_cate = WorryCategoryModel.objects.get(cate_name="일상").id
        last_cate = WorryCategoryModel.objects.get(cate_name="육아").id

        worry_obj1 = WorryBoardModel.objects.create(author=user, content="ttttt", category_id=first_cate)
        worry_obj2 = WorryBoardModel.objects.create(author=user, content="ttttt", category_id=last_cate)

        LetterModel.objects.create(
            letter_author_id=test_user.id,
            worryboard_id=worry_obj1.id,
            title="test",
            content="test",
        )
        LetterModel.objects.create(
            letter_author_id=test_user.id,
            worryboard_id=worry_obj2.id,
            title="test",
            content="test",
        )

        with self.assertRaises(UserModel.DoesNotExist):
            my_letter_count(UserModel.objects.get(id=9999).id)

    def test_worryboard_union_service(self) -> None:
        """
        카테고리별 최신순으로 3개씩 get하는 함수를 검증
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
        UserProfileModel.objects.create(user=user)

        category_list = ["일상", "연애", "학업", "가족", "인간관계", "육아"]
        for cate_name in category_list:
            WorryCategoryModel.objects.create(cate_name=cate_name)

        first_cate = WorryCategoryModel.objects.get(cate_name="일상").id
        last_cate = WorryCategoryModel.objects.get(cate_name="육아").id

        for woory_board_count in range(5):
            for cate_idx in range(first_cate, last_cate + 1):
                WorryBoardModel.objects.create(author_id=user.id, content="ttttt", category_id=cate_idx)

        worry_categories = WorryCategoryModel.objects.prefetch_related("worryboard_set").all()
        worry_worryboard_union(worry_categories)

        test_board = WorryBoardModel.objects.filter(category_id=first_cate).order_by("-create_date")[:3]

        count = 0
        for worry_union_idx in worry_worryboard_union(worry_categories):
            if worry_union_idx in test_board:
                count += 1

        self.assertEqual(18, worry_worryboard_union(worry_categories).count())
        self.assertEqual(3, count)

    def test_when_not_queryset_worryboard_union_service(self) -> None:
        """
        카테고리별 최신순으로 3개씩 get하는 함수를 검증
        case: 쿼리셋이 아닌 obj를 조회 했을 때
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
        UserProfileModel.objects.create(user=user)

        category_list = ["일상", "연애", "학업", "가족", "인간관계", "육아"]
        for cate_name in category_list:
            WorryCategoryModel.objects.create(cate_name=cate_name)

        first_cate = WorryCategoryModel.objects.get(cate_name="일상").id
        last_cate = WorryCategoryModel.objects.get(cate_name="육아").id

        for woory_board_count in range(5):
            for cate_idx in range(first_cate, last_cate + 1):
                WorryBoardModel.objects.create(author_id=user.id, content="ttttt", category_id=cate_idx)

        worry_categories = WorryCategoryModel.objects.prefetch_related("worryboard_set").all()

        with self.assertRaises(WorryCategoryModel.MultipleObjectsReturned):
            worry_worryboard_union(worry_categories.get())

    def test_live_reveiw_list_service(self) -> None:
        """
        실시간 리뷰  순으로 편지리뷰 get하는 함수를 검증
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
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

        for worry_idx in range(first_worry_obj, last_worry_obj):
            LetterModel.objects.create(
                letter_author=user,
                worryboard_id=worry_idx,
                title="test",
                content="test",
            )

        first_letter_obj = LetterModel.objects.order_by("create_date")[:1].get().id
        last_letter_obj = LetterModel.objects.order_by("-create_date")[:1].get().id

        for letter_review_count in range(first_letter_obj, last_letter_obj):
            LetterReviewModel.objects.create(
                review_author=user,
                letter_id=letter_review_count,
                content="test",
                grade=50,
            )

        create_order_live_reviews = live_review_list_service()
        live_reivew = LetterReviewModel.objects.order_by("-create_date")[:10]
        self.assertEqual(10, create_order_live_reviews.count())
        self.assertEqual(True, live_reivew[0] == create_order_live_reviews[0])
        self.assertEqual(50, create_order_live_reviews[0].grade)

    def test_best_reveiw_list_service(self) -> None:
        """
        베스트 리뷰 순으로 편지리뷰 get하는 함수를 검증
        """
        user = UserModel.objects.create(username="hajin", nickname="hajin")
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

        for worry_idx in range(first_worry_obj, last_worry_obj):
            LetterModel.objects.create(
                letter_author=user,
                worryboard_id=worry_idx,
                title="test",
                content="test",
            )

        first_letter_obj = LetterModel.objects.order_by("create_date")[:1].get().id
        last_letter_obj = LetterModel.objects.order_by("-create_date")[:1].get().id

        for letter_review_count in range(first_letter_obj, last_letter_obj):
            LetterReviewModel.objects.create(
                review_author=user,
                letter_id=letter_review_count,
                content="test",
                grade=100,
            )

        get_cate = WorryCategoryModel.objects.get(cate_name="일상")
        grade_test_worry = WorryBoardModel.objects.create(author_id=user.id, content="test", category_id=get_cate.id)
        grade_test_letter = LetterModel.objects.create(
            letter_author=user,
            worryboard_id=grade_test_worry.id,
            title="test",
            content="test",
        )
        LetterReviewModel.objects.create(
            review_author=user,
            letter_id=grade_test_letter.id,
            content="test",
            grade=200,
        )

        grade_order_best_reviews = best_review_list_service()
        best_review = LetterReviewModel.objects.order_by("-grade")[:10]

        self.assertEqual(10, grade_order_best_reviews.count())
        self.assertEqual(True, best_review[0] == grade_order_best_reviews[0])
        self.assertEqual(200, grade_order_best_reviews[0].grade)
        self.assertEqual(100, grade_order_best_reviews[len(grade_order_best_reviews) - 1].grade)

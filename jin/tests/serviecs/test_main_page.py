from django.test import TestCase

from jin.models import Letter as LetterModel
from jin.models import LetterReview as LetterReviewModel
from jin.models import WorryCategory as WorryCategoryModel
from jin.services.main_gage_service import (
    best_review_list_service,
    live_review_list_service,
    worry_obj_my_letter,
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

        worry_obj1 = WorryBoardModel.objects.create(
            author=user, content="ttttt", category_id=first_cate
        )
        worry_obj2 = WorryBoardModel.objects.create(
            author=user, content="ttttt", category_id=last_cate
        )

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

        my_worrys = worry_obj_my_letter(user.id)

        letter_count = 0
        for letter_get in my_worrys:
            try:
                if letter_get.letter.is_read == False:
                    letter_count += 1
            except WorryBoardModel.letter.RelatedObjectDoesNotExist:
                break
        self.assertEqual("일상", WorryCategoryModel.objects.get(id=first_cate).cate_name)
        self.assertEqual(
            test_user.id, LetterModel.objects.get(id=letter_obj1.id).letter_author.id
        )
        self.assertEqual(2, letter_count)

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

        worry_obj1 = WorryBoardModel.objects.create(
            author=user, content="ttttt", category_id=first_cate
        )
        worry_obj2 = WorryBoardModel.objects.create(
            author=user, content="ttttt", category_id=last_cate
        )

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

        fake_user = UserModel.objects.filter(id=9999)

        with self.assertRaises(UserModel.DoesNotExist):
            worry_obj_my_letter(fake_user.get().id)

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
                WorryBoardModel.objects.create(
                    author_id=user.id, content="ttttt", category_id=cate_idx
                )

        woory_categorys = WorryCategoryModel.objects.prefetch_related(
            "worryboard_set"
        ).all()
        worry_worryboard_union(woory_categorys)

        test_board = WorryBoardModel.objects.filter(category_id=first_cate).order_by(
            "-create_date"
        )[:3]

        self.assertEqual(18, worry_worryboard_union(woory_categorys).count())
        for i in range(test_board.count()):
            self.assertEqual(
                True, worry_worryboard_union(woory_categorys)[i] == test_board[i]
            )

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
                WorryBoardModel.objects.create(
                    author_id=user.id, content="ttttt", category_id=cate_idx
                )

        worry_categorys = WorryCategoryModel.objects.prefetch_related(
            "worryboard_set"
        ).all()

        with self.assertRaises(WorryCategoryModel.MultipleObjectsReturned):
            worry_worryboard_union(worry_categorys.get())

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
                WorryBoardModel.objects.create(
                    author_id=user.id, content="test", category_id=cate_idx
                )

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

        live_review_list_service()
        live_reivew = LetterReviewModel.objects.order_by("-create_date")[:10]
        self.assertEqual(10, live_review_list_service().count())
        self.assertEqual(True, live_reivew[0] == live_review_list_service()[0])
        self.assertEqual(50, live_review_list_service()[0].grade)

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
                WorryBoardModel.objects.create(
                    author_id=user.id, content="test", category_id=cate_idx
                )

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
        grade_test_worry = WorryBoardModel.objects.create(
            author_id=user.id, content="test", category_id=get_cate.id
        )
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

        best_review_list_service()
        best_review = LetterReviewModel.objects.order_by("-grade")[:10]

        self.assertEqual(10, best_review_list_service().count())
        self.assertEqual(True, best_review[0] == best_review_list_service()[0])
        self.assertEqual(200, best_review_list_service()[0].grade)
        self.assertEqual(
            100, best_review_list_service()[len(best_review_list_service()) - 1].grade
        )

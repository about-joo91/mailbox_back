from django.test import TestCase
from rest_framework.exceptions import ValidationError

from main_page.models import WorryCategory
from user.models import User as UserModel
from worry_board.models import RequestStatus as RequestStatusModel
from worry_board.models import WorryBoard as WorryBoardModel
from worry_board.services.worry_board_service import (
    check_is_it_clean_text,
    create_worry_board_data,
    delete_worry_board_data,
    get_paginated_worry_board_data,
    update_worry_board_data,
)


class TestWorryBoardService(TestCase):
    """
    Worry_Board 서비스 함수들을 검증하는 클래스
    """

    @classmethod
    def setUpTestData(cls):
        RequestStatusModel.objects.create(status="요청")
        RequestStatusModel.objects.create(status="요청취소")

    def test_when_success_get_worry_board_data(self):
        """
        pagenation을 통하여 worry_board를 가져오는 함수에 대한 검증
        """
        user = UserModel.objects.create(username="Ko", nickname="Ko")
        category = WorryCategory.objects.create(cate_name="일상")
        page_num = 1
        WorryBoardModel.objects.create(author=user, category=category, content="get테스트")
        paginated_worry_board, total_count = get_paginated_worry_board_data(page_num, category.id)

        self.assertEqual(1, total_count)
        self.assertEqual(
            WorryBoardModel.objects.all()[0].id,
            WorryBoardModel.objects.get(author=user).id,
        )
        self.assertEqual(paginated_worry_board[0], WorryBoardModel.objects.filter(author=user)[0])

    def test_when_success_create_worry_board_data(self) -> None:
        """
        worry_board_data를 생성하는 함수가 정상적으로 작동되었을 때에 대한 검증
        """

        user = UserModel.objects.create(username="Ko", nickname="Ko")
        category = WorryCategory.objects.create(cate_name="일상")
        create_data = {"category": category.id, "content": "생성테스트"}
        if check_is_it_clean_text(create_data["content"]):
            with self.assertNumQueries(2):
                create_worry_board_data(author=user, create_data=create_data)

        self.assertEqual(
            WorryBoardModel.objects.all()[0].id,
            WorryBoardModel.objects.get(author=user).id,
        )

    def test_when_post_including_swear_word_in_create_worry_board_data(self) -> None:
        """
        worry_board_data를 작성할 때 욕설이 포함되어 있을 때에 대한 검증
        """
        user = UserModel.objects.create(username="Ko", nickname="Ko")
        category = WorryCategory.objects.create(cate_name="일상")
        create_data = {"category": category.id, "content": "바보같은놈"}
        if check_is_it_clean_text(create_data["content"]):
            create_worry_board_data(author=user, create_data=create_data)

        with self.assertRaises(WorryBoardModel.DoesNotExist):
            WorryBoardModel.objects.get(author=user).id

    def test_when_over_content_lengths_90_in_create_worry_board_data(self) -> None:
        """
        worry_board_data를 생성하는 함수가
        content의 제한수인 90을 넘겼을 경우에 대한 검증
        """
        user = UserModel.objects.create(username="Ko", nickname="Ko")
        category = WorryCategory.objects.create(cate_name="일상")
        create_data = {"category": category.id, "content": str("a" * 100)}

        with self.assertRaises(ValidationError):
            if check_is_it_clean_text(create_data["content"]):
                create_worry_board_data(author=user, create_data=create_data)

    def test_when_success_update_worry_board_data(self) -> None:
        """
        worry_board_data를 수정하는 함수가 정상적으로 작동되었을 때에 대한 검증
        """

        user = UserModel.objects.create(username="Ko", nickname="Ko")
        category = WorryCategory.objects.create(cate_name="일상")
        user_worry_board = WorryBoardModel.objects.create(author=user, category=category, content="수정전")
        update_data = {"category": category.id, "content": "수정함"}
        if check_is_it_clean_text(update_data["content"]):
            with self.assertNumQueries(3):
                update_worry_board_data(worry_board_id=user_worry_board.id, update_data=update_data)

        self.assertEqual(user_worry_board.id, WorryBoardModel.objects.get(author=user).id)

    def test_when_post_including_swear_word_in_update_worry_board_data(self) -> None:
        """
        worry_board_data를 수정하는 함수가
        욕설을 포함하였을 경우에 대한 검증
        """

        user = UserModel.objects.create(username="Ko", nickname="Ko")
        category = WorryCategory.objects.create(cate_name="일상")
        user_worry_board = WorryBoardModel.objects.create(author=user, category=category, content="수정전")
        update_data = {"category": category.id, "content": "바보같은놈"}
        if check_is_it_clean_text(update_data["content"]):
            update_worry_board_data(worry_board_id=user_worry_board.id, update_data=update_data)

        with self.assertRaises(WorryBoardModel.DoesNotExist):
            WorryBoardModel.objects.get(content="바보같은놈")

    def test_when_post_does_not_exist_in_update_worry_board_data(self) -> None:
        """
        worry_board_daga를 수정할 때 worry_board가 없는 경우에 대한 검증
        """
        category = WorryCategory.objects.create(cate_name="일상")
        update_data = {"category": category.id, "content": "수정함"}
        if check_is_it_clean_text(update_data["content"]):
            with self.assertRaises(WorryBoardModel.DoesNotExist):
                update_worry_board_data(worry_board_id=10, update_data=update_data)
        with self.assertRaises(WorryBoardModel.DoesNotExist):
            update_worry_board_data(WorryBoardModel.objects.get(content="수정함"))

    def test_when_success_delete_worry_board_data(self) -> None:
        """
        worry_board_data를 삭제하는 함수가 정상적으로 작동 되었을 때에 대한 검증
        """
        user = UserModel.objects.create(username="Ko", nickname="Ko")
        category = WorryCategory.objects.create(cate_name="일상")
        user_worry_board = WorryBoardModel.objects.create(author=user, category=category, content="삭제할 데이터")
        with self.assertNumQueries(4):
            delete_worry_board_data(author=user, worry_board_id=user_worry_board.id)

        self.assertEqual(0, WorryBoardModel.objects.count())

    def test_delete_worry_board_data_which_doesnot_exist(self) -> None:
        """
        worry_board_data를 삭제하는 함수가 정상적으로 작동 되었을 때에 대한 검증
        case : 없는 worry_board를 삭제하려고 할 때
        """
        user = UserModel.objects.create(username="Ko", nickname="Ko")

        with self.assertRaises(WorryBoardModel.DoesNotExist):
            delete_worry_board_data(author=user, worry_board_id=9999)
        self.assertEqual(0, WorryBoardModel.objects.count())

    def test_when_function_including_swear_word_in_check_is_it_clean_text(self) -> None:
        """
        욕설을 검증하는 함수가 제대로 작동을 하는지 검증
        """
        data = {"content": "바보같은놈"}
        self.assertEqual(False, check_is_it_clean_text(data["content"]))

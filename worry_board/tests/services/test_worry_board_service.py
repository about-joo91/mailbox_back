from django.test import TestCase
import json
from rest_framework.test import APIClient


from user.models import User as UserModel
from worry_board.models import WorryBoard as WorryBoardModel
from main_page.models import WorryCategory
from worry_board.services.worry_board_service import(
    create_worry_board_data,
    get_paginated_worry_board_data,
    create_worry_board_data,
    update_worry_board_data,
    delete_worry_board_data,
    check_is_it_clean_text
)

class TestWorryBoardService(TestCase):
    """
    Worry_Board 서비스 함수들을 검증하는 클래스
    """

    def test_when_success_get_worry_board_data(self):
        """
        pagenation을 통하여 worry_board를 가져오는 함수에 대한 검증
        """
        user = UserModel.objects.create(username = "Ko", nickname="Ko")
        category = WorryCategory.objects.create(cate_name="일상")
        page_num = 1
        WorryBoardModel.objects.create(author=user, category=category, content="get테스트")
        paginated_worry_board, total_count = get_paginated_worry_board_data(page_num, category.id)
        
        self.assertEqual(1, total_count)
        self.assertEqual(WorryBoardModel.objects.all()[0].id, WorryBoardModel.objects.get(author = user).id)
        self.assertEqual(paginated_worry_board[0], WorryBoardModel.objects.filter(author = user)[0])
    

    def test_when_success_create_worry_board_data(self) -> None:
        """
        worry_board_data를 생성하는 함수가 정상적으로 작동되었을 때에 대한 검증
        """
        user = UserModel.objects.create(username="Ko", nickname="Ko")
        category = WorryCategory.objects.create(cate_name="일상")
        create_data ={
            "category" : category.id,
            "content" : "생성테스트"
        }
        if check_is_it_clean_text(create_data["content"]):
            create_worry_board_data(create_data=create_data, author=user)

        self.assertEqual(1, WorryBoardModel.objects.get(author = user).id)



    def test_when_success_update_worry_board_data(self) -> None:
        """
        worry_board_data를 업데이트 하는 함수가 정상적으로 작동되었을 때에 대한 검증
        """

        user = UserModel.objects.create(username="Ko", nickname="Ko")
        category = WorryCategory.objects.create(cate_name="일상")
        user_worry_board = WorryBoardModel.objects.create(author=user, category=category, content="수정전")
        update_data = {
            "category" : category.id,
            "content" : "수정함"
        }
        update_worry_board_data(worry_board_id = user_worry_board.id, update_worry_board_data = update_data)
        
        self.assertEqual(user_worry_board.id, WorryBoardModel.objects.get(author=user).id)

    def test_when_success_delete_worry_board_data(self) -> None:
        """
        worry_board_data를 삭제하는 함수가 정상적으로 작동 되었을 때에 대한 검증
        """
        user = UserModel.objects.create(username="Ko", nickname="Ko")
        category = WorryCategory.objects.create(cate_name="일상")
        user_worry_board = WorryBoardModel.objects.create(author=user, category=category, content="삭제할 데이터")
        delete_worry_board_data(worry_board_id=user_worry_board.id, author=user)

        self.assertEqual(0, WorryBoardModel.objects.count())

    def test_when_post_including_swear_word_in_create_worry_board_data(self) -> None:
        """
        worry_board_data를 작성할 때 욕설이 포함되어 있을 때에 대한 검증
        """
        user = UserModel.objects.create(username="Ko", nickname="Ko")
        category = WorryCategory.objects.create(cate_name="일상")
        create_data ={
            "category" : category.id,
            "content" : "생성테스트"
        }
        create_worry_board_data(create_data=create_data, author=user)

        self.assertEqual(1, WorryBoardModel.objects.get(author = user).id)






from django.test import TestCase

from user.models import User as UserModel
from board.models import Board as BoardModel
from board.services.board_service import (
    check_is_it_clean_text, 
    create_board_data, 
    delete_board_data, 
    get_paginated_board_data, 
    update_board_data
)



class TestBoardService(TestCase):
    """
    BoardView의 service 함수를 검증하는 클래스
    """
    
    def test_check_is_it_clean_text(self):
        """
        비속어 필터링 함수 체크
        case: 비속어가 포함되어 있지 않은 경우
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        request_data = {"title": "title", "content": "봄날의 햇살", "author": user.id}
        result = check_is_it_clean_text(request_data["content"])
        
        self.assertTrue(result)
    
    
    def test_check_is_it_clean_text_when_contents_include_swear_word(self) -> None:
        """
        비속어 필터링 함수 체크
        case: 비속어가 포함되어 있는 경우
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        request_data = {"title": "title", "content": "바보 멍청이", "author": user.id}
        result = check_is_it_clean_text(request_data["content"])
        
        self.assertFalse(result)
        
        
    def test_get_paginated_board_data(self) -> None:
        """
        page_num을 통해서 board 데이터를 가져오는 service 함수 검증
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        BoardModel.objects.create(title="title", content="content", author=user)

        paginated_board, total_count = get_paginated_board_data(1)
        
        with self.assertNumQueries(1):
            get_paginated_board_data(1)
        
        self.assertEqual(1, total_count)
        
        
    def test_create_board_data(self) -> None:
        """
        board 데이터를 작성하는 service 함수 검증
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        request_data = {"title": "title", "content": "content", "author": user.id}
        
        with self.assertNumQueries(2):
            create_board_data(request_data, user.id)
        
        board = BoardModel.objects.get(author=user.id)
        
        self.assertEqual(1, BoardModel.objects.all().count())
        self.assertEqual(board.title, "title")
        self.assertEqual(board.content, "content")
    
    
    def test_update_board_data(self) -> None:
        """
        board 데이터를 업데이트 하는 service 함수 검증
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        user_board = BoardModel.objects.create(
            title="title", content="content", author=user
        )
        request_data = {"title": "수정된 제목", "content": "수정된 내용", "author": user.id}

        with self.assertNumQueries(4):
            update_board_data(user_board.id, request_data, user.id)
            
        updated_board = BoardModel.objects.get(id=user_board.id)
        
        self.assertEqual(updated_board.title, "수정된 제목")
        self.assertEqual(updated_board.content, "수정된 내용")
        
    
    def test_delete_board_data(self) -> None:
        """
        board 데이터를 삭제하는 service 함수 검증
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        user_board = BoardModel.objects.create(
            title="title", content="content", author=user
        )
        
        self.assertEqual(1, BoardModel.objects.all().count())
        
        with self.assertNumQueries(5):
            delete_board_data(user_board.id, user.id)
        
        self.assertEqual(0, BoardModel.objects.all().count())
        
        
        
        
        
        
    
    
    
    
    
    
    


    
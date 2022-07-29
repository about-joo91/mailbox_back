from django.forms import ValidationError
from django.test import TestCase
from rest_framework import exceptions

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
        
    def test_get_paginated_board_data_with_unauthenticated_user(self) -> None:
        """
        page_num을 통해서 board 데이터를 가져오는 service 함수 검증
        case: 없는 페이지번호로 함수를 부를 경우
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        BoardModel.objects.create(title="title", content="content", author=user)

        with self.assertRaises(TypeError):
            create_board_data(2)
        
        
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
        
        
    def test_create_board_data_with_unauthenticated_user(self) -> None:
        """
        board 데이터를 작성하는 service 함수 검증
        case: 로그인 하지 않은 사용자가 post하는 경우
        """
        request_data = {"title": "title", "content": "content"}
        
        with self.assertRaises(TypeError):
            create_board_data(request_data)

    def test_create_board_data_when_title_with_over_limited_num(self) -> None:
        """
        board 데이터를 작성하는 service 함수 검증
        case: 작성한 제목이 제한 글자수(30자) 이상인 경우
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        request_data = {
            "title": "30자 이상입니다. 30자 이상입니다. 30자 이상입니다",
            "content": "content",
            "author": user.id,
        }
        with self.assertRaises(exceptions.ValidationError):
            create_board_data(request_data, user.id)
            
            
    def test_create_board_data_when_content_with_over_limited_num(self) -> None:
        """
        board 데이터를 작성하는 service 함수 검증
        case: 작성한 내용이 제한 글자수(500자) 이상인 경우
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        request_data = {
            "title": "title",
            "content": "500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. \
            500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 \
            이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. \
            500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. \
            500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. \
            500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. \
            500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. \
            500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. \
            500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니",
            "author": user.id,
        }
        with self.assertRaises(exceptions.ValidationError):
            create_board_data(request_data, user.id)
        

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
        
        
    def test_update_board_data_with_unauthenticated_user(self) -> None:
        """
        board 데이터를 업데이트 하는 service 함수 검증
        case: 로그인 하지 않은 사용자가 put(수정)하는 경우
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        user_board = BoardModel.objects.create(
            title="title", content="content", author=user
        )
        request_data = {"title": "수정된 제목", "content": "수정된 내용",  "author": user.id}
        
        with self.assertRaises(exceptions.PermissionDenied):
            update_board_data(user_board.id, request_data, None)
            
    
    def test_update_board_data_which_doesnot_exist(self) -> None:
        """
        board 데이터를 업데이트 하는 service 함수 검증
        case: 없는 게시글을 수정하려고 할 때
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        request_data = {"title": "수정된 제목", "content": "수정된 내용", "author": user.id}

        with self.assertRaises(BoardModel.DoesNotExist):
            update_board_data(None, request_data, user.id)
    
    def test_update_board_data_by_not_author(self) -> None:
        """
        board 데이터를 업데이트 하는 service 함수 검증
        case: 게시물을 쓴 사용자가 아닌 사람이 수정을 하려는 경우
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        author = UserModel.objects.create(
            username="won2", password="1234", nickname="won2"
        )
        user_board = BoardModel.objects.create(
            title="title", content="content", author=author
        )
        request_data = {"title": "수정된 제목", "content": "수정된 내용",  "author": author.id}
        
        with self.assertRaises(exceptions.PermissionDenied):
            update_board_data(user_board.id, request_data, user.id) 


    def test_update_board_data_when_title_with_over_limited_num(self) -> None:
        """
        board 데이터를 업데이트 하는 service 함수 검증
        case: 제목이 제한 글자수 이상인 경우
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        user_board = BoardModel.objects.create(
            title="title", content="content", author=user
        )
        request_data = {
            "title": "30자 이상입니다. 30자 이상입니다. 30자 이상입니다",
            "content": "content",
            "author": user.id,
        }
        with self.assertRaises(exceptions.ValidationError):
            update_board_data(user_board.id, request_data, user.id)
            
            
    def test_update_board_data_when_content_with_over_limited_num(self) -> None:
        """
        board 데이터를 업데이트 하는 service 함수 검증
        case: 내용이 제한 글자수 이상인 경우
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        user_board = BoardModel.objects.create(
            title="title", content="content", author=user
        )
        request_data = {
            "title": "title",
            "content": "500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. \
            500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 \
            이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. \
            500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. \
            500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. \
            500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. \
            500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. \
            500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니다. \
            500자 이상입니다. 500자 이상입니다. 500자 이상입니다. 500자 이상입니",
            "author": user.id,
        }
        with self.assertRaises(exceptions.ValidationError):
            update_board_data(user_board.id, request_data, user.id)
    
    
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
        
        
    def test_delete_board_data_with_unauthenticated_user(self) -> None:
        """
        board 데이터를 삭제하는 service 함수 검증
        case : 로그인 하지 않은 사용자가 삭제하려는 경우
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        user_board = BoardModel.objects.create(
            title="title", content="content", author=user
        )
        with self.assertRaises(exceptions.PermissionDenied):
            delete_board_data(user_board.id, None)
        
        
    def test_delete_board_data_which_doesnot_exist(self) -> None:
        """
        board 데이터를 삭제하는 service 함수 검증
        case: 없는 게시글을 삭제하려고 할 때
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        
        with self.assertRaises(BoardModel.DoesNotExist):
            delete_board_data(None, user.id)
            
    def test_delete_board_data_by_not_author(self) -> None:
        """
        board 데이터를 삭제하는 service 함수 검증
        case: 게시물을 쓴 사용자가 아닌 사람이 삭제 하려는 경우
        """
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        author = UserModel.objects.create(
            username="won2", password="1234", nickname="won2"
        )
        user_board = BoardModel.objects.create(
            title="title", content="content", author=author
        )
        with self.assertRaises(exceptions.PermissionDenied):
            delete_board_data(user_board.id, user.id)
        
    
        
        
        
        
        
        
    
    
    
    
    
    
    


    
from django.test import TestCase

import json

from rest_framework.test import APIClient

from board.models import Board as BoardModel
from user.models import User as UserModel


class TestBoardService(TestCase):
    """
    BoardView의 service를 검증하는 클래스
    """
    
    def test_including_swear_word_in_post_board_content(self) -> None:
        """
        BoardView의 post 함수를 검증하는 함수
        case : 욕설을 포함한 내용을 post하는 경우
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        request_data = {"title": "title", "content": "바보 멍청이", "author": user.id}

        client.force_authenticate(user=user)
        url = "/board/"
        response = client.post(
            url, data=json.dumps(request_data), content_type="application/json"
        )
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다")

    def test_exceeding_limited_num_of_char_on_post_board_title(self) -> None:
        """
        BoardView의 post 함수를 검증하는 함수
        case : 제목에 제한된 글자수(30자)를 초과하여 post하는 경우
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        request_data = {
            "title": "30자 이상입니다. 30자 이상입니다. 30자 이상입니다",
            "content": "content",
            "author": user.id,
        }

        client.force_authenticate(user=user)
        url = "/board/"
        response = client.post(
            url, data=json.dumps(request_data), content_type="application/json"
        )
        print(response)
        result = response.json()
        print(result)

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드의 글자 수가 30 이하인지 확인하십시오.", result["detail"])


    def test_exceeding_limited_num_of_char_on_post_board_content(self) -> None:
        """
        BoardView의 post 함수를 검증하는 함수
        case : 내용에 제한된 글자수를 초과하여 post하는 경우
        """
        client = APIClient()
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

        client.force_authenticate(user=user)
        url = "/board/"
        response = client.post(
            url, data=json.dumps(request_data), content_type="application/json"
        )
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드의 글자 수가 500 이하인지 확인하십시오.", result["detail"])
        
        
    def test_exceeding_limited_num_of_char_on_post_board_title_and_content(self) -> None:
        """
        BoardView의 post 함수를 검증하는 함수
        case: 작성한 board의 제목과 내용이 제한 글자 수(각 30, 500자)를 초과했을 경우
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        request_data = {
            "title": "30자 이상입니다. 30자 이상입니다. 30자 이상입니다",
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

        client.force_authenticate(user=user)
        url = "/board/"
        response = client.post(
            url, data=json.dumps(request_data), content_type="application/json"
        )
        result = response.json()
        print(result)

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드의 글자 수가 500 이하인지 확인하십시오.", result["detail"])
        self.assertIn("이 필드의 글자 수가 30 이하인지 확인하십시오.", result["detail"])



    def test_including_swear_word_in_put_board_content(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        case: 수정한 내용이 욕설을 포함한 내용일 경우
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        user_board = BoardModel.objects.create(
            title="title", content="content", author=user
        )
        request_data = {"title": "수정된 제목", "content": "바보 멍청이", "author": user.id}

        client.force_authenticate(user=user)
        url = "/board/" + str(user_board.id)
        response = client.put(
            url, data=json.dumps(request_data), content_type="application/json"
        )
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "부적절한 내용이 담겨있어 게시글을 수정 할 수 없습니다")
        
        
    def test_exceeding_limited_num_of_char_on_put_board_title(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        case: 수정한 제목이 제한 글자 수(30자)를 초과했을 경우
        """
        client = APIClient()
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

        client.force_authenticate(user=user)
        url = "/board/" + str(user_board.id)
        response = client.put(
            url, data=json.dumps(request_data), content_type="application/json"
        )
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드의 글자 수가 30 이하인지 확인하십시오.", result["detail"])
    
    
    def test_exceeding_limited_num_of_char_on_put_board_content(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        case: 수정한 내용이 제한 글자 수(500자)를 초과했을 경우
        """
        
        client = APIClient()
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

        client.force_authenticate(user=user)
        url = "/board/" + str(user_board.id)
        response = client.put(
            url, data=json.dumps(request_data), content_type="application/json"
        )
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드의 글자 수가 500 이하인지 확인하십시오.", result["detail"])
        
        
    def test_exceeding_limited_num_of_char_on_put_board_title_and_content(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        case: 수정한 제목과 내용이 제한 글자 수(각 30, 500자)를 초과했을 경우
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        user_board = BoardModel.objects.create(
            title="title", content="content", author=user
        )
        request_data = {
            "title": "30자 이상입니다. 30자 이상입니다. 30자 이상입니다",
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

        client.force_authenticate(user=user)
        url = "/board/" + str(user_board.id)
        response = client.put(
            url, data=json.dumps(request_data), content_type="application/json"
        )
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드의 글자 수가 30 이하인지 확인하십시오.", result["detail"])
        self.assertIn("이 필드의 글자 수가 500 이하인지 확인하십시오.", result["detail"])

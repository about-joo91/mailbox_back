import json

from rest_framework.test import APIClient, APITestCase

from board.models import Board as BoardModel
from board.services.board_service import get_paginated_board_data
from user.models import User as UserModel


class TestBoardAPI(APITestCase):
    """
    BoardView의 API를 검증하는 클래스
    """

    def test_get_board_list(self) -> None:
        """
        BoardView의 get 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        BoardModel.objects.create(title="title", content="content", author=user)

        client.force_authenticate(user=user)
        url = "/board/?page_num=1"
        response = client.get(url)
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["total_count"], 1)
        

    def test_when_is_user_is_unauthenticated_in_get_board_list(self) -> None:
        """
        BoardView의 get 함수를 검증하는 함수
        case : 로그인하지 않은 사용자가 조회하는 경우
        """
        client = APIClient()

        url = "/board/?page_num=1"
        response = client.get(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual(
            result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다."
        )

    def test_when_parameter_doesnot_exist_in_get_board_list(self) -> None:
        """
        BoardView의 get 함수를 검증하는 함수
        case : 빈파라미터를 넣은 경우
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        BoardModel.objects.create(title="title", content="content", author=user)

        client.force_authenticate(user=user)
        
        with self.assertRaises(TypeError):
            get_paginated_board_data()
            
        url = "/board/"
        response = client.get(url)
        result = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "게시판을 조회할 수 없습니다. 다시 시도해주세요.")


    def test_post_board_content(self) -> None:
        """
        BoardView의 post 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        request_data = {"title": "title", "content": "content", "author": user.id}

        client.force_authenticate(user=user)
        url = "/board/"
        response = client.post(
            url, data=json.dumps(request_data), content_type="application/json"
        )
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "게시글이 생성되었습니다.")
        

    def test_when_unauthenticated_user_in_post_board_content(self) -> None:
        """
        BoardView의 post 함수를 검증하는 함수
        case : 로그인하지 않은 사용자가 post하는 경우
        """
        client = APIClient()
        request_data = {"title": "title", "content": "content"}

        url = "/board/"
        response = client.post(
            url, data=json.dumps(request_data), content_type="application/json"
        )
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual(
            result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다."
        )
    
    
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
        result = response.json()


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

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드의 글자 수가 500 이하인지 확인하십시오.", result["detail"])
        self.assertIn("이 필드의 글자 수가 30 이하인지 확인하십시오.", result["detail"])


    
    def test_put_board_content(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        user_board = BoardModel.objects.create(
            title="title", content="content", author=user
        )
        request_data = {"title": "수정된 제목", "content": "수정된 내용", "author": user.id}

        client.force_authenticate(user=user)
        url = "/board/" + str(user_board.id)
        response = client.put(
            url, data=json.dumps(request_data), content_type="application/json"
        )
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "게시글이 수정되었습니다.")
        
    
    def test_when_unauthenticated_user_put_board_content(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        case : 로그인하지 않은 사용자가 put하는 경우
        """
        
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        user_board = BoardModel.objects.create(
            title="title", content="content", author=user
        )
        request_data = {"title": "수정된 제목", "content": "수정된 내용", "author": user.id}

        
        url = "/board/" + str(user_board.id)
        response = client.put(
            url, data=json.dumps(request_data), content_type="application/json"
        )
        result = response.json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다."
        )
    
    
    def test_when_not_author_put_board_content(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        case : 게시물을 쓴 사용자가 아닌 사람이 수정을 하려는 경우
        """
        
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        author = UserModel.objects.create(
            username="won2", password="1234", nickname="won2"
        )
        author_board = BoardModel.objects.create(
            title="title", content="content", author=author
        )
        request_data = {"title": "수정된 제목", "content": "수정된 내용", "author": author.id}

        client.force_authenticate(user=user)
        url = "/board/" + str(author_board.id)
        response = client.put(
            url, data=json.dumps(request_data), content_type="application/json"
        )
        result = response.json()
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(result["detail"], "게시글 수정 권한이 없습니다")
        
    def test_when_parameter_doesnot_exist_in_put_board_list(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        case : 빈파라미터를 넣은 경우
        """
        
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        user_board = BoardModel.objects.create(title="title", content="content", author=user)
        
        request_data = {"title": "수정된 제목", "content": "수정된 내용", "author": user.id}

        client.force_authenticate(user=user)
        url = "/board/" 
        
        response = client.put(
            url, data=json.dumps(request_data), content_type="application/json"
        )
        result = response.json()
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"],"게시글이 존재하지 않습니다")
        
    
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

    
        
    def test_delete_board_content(self) -> None:
        """
        BoardView의 delete 함수를 검증하는 함수
        """
        
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        user_board = BoardModel.objects.create(
            title="title", content="content", author=user
        )
        client.force_authenticate(user=user)
        url = "/board/" + str(user_board.id)
        response = client.delete(url)
        result = response.json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "게시글이 삭제되었습니다.")
        
        
    def test_when_unauthenticated_user_delete_board_content(self) -> None:
        """
        BoardView의 delete 함수를 검증하는 함수
        case: 로그인하지 않은 사용자가 게시물을 삭제하려는 경우
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        user_board = BoardModel.objects.create(
            title="title", content="content", author=user
        )
        url = "/board/" + str(user_board.id)
        response = client.delete(url)
        result = response.json()
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다."
        )
        
        
    def test_when_not_author_delete_board_content(self) -> None:
        """
        BoardView의 delete 함수를 검증하는 함수
        case: 게시물을 쓰지 않은 사람이 게시물을 삭제하려는 경우
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        author = UserModel.objects.create(
            username="won2", password="1234", nickname="won2"
        )
        author_board = BoardModel.objects.create(
            title="title", content="content", author=author
        )
        
        client.force_authenticate(user=user)
        url = "/board/" + str(author_board.id)
        response = client.delete(url)
        result = response.json()
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(result["detail"], "게시글 삭제 권한이 없습니다")


    def test_when_parameter_doesnot_exist_in_delete_board_list(self) -> None:
        """
        BoardView의 delete 함수를 검증하는 함수
        case : 빈파라미터를 넣은 경우
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )

        client.force_authenticate(user=user)
        url = "/board/"
        response = client.delete(url)
        result = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "게시글이 존재하지 않습니다")
        
        
        
    def test_when_post_doesnot_exist_in_delete_board_list(self) -> None:
        """
        BoardView의 delete 함수를 검증하는 함수
        case : 존재하지 않는 게시물을 삭제하려는 경우
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="won1", password="1234", nickname="won"
        )
        
        client.force_authenticate(user=user)
        url = "/board/"+ str(9999)
        response = client.delete(url)
        result = response.json()
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "게시글이 존재하지 않습니다")
import json

from rest_framework.test import APIClient, APITestCase

from board.models import Board as BoardModel
from board.models import BoardComment as BoardCommentModel
from board.services.board_service import get_paginated_board_data
from user.models import MongleGrade, MongleLevel
from user.models import User as UserModel
from user.models import UserProfile


class TestBoardAPI(APITestCase):
    """
    BoardView의 API를 검증하는 클래스
    """

    @classmethod
    def setUpTestData(cls):
        cur_user = UserModel.objects.create(username="ko", nickname="ko")
        not_cur_user = UserModel.objects.create(username="not_cur_user", nickname="not_cur_user")

        UserProfile.objects.create(user=cur_user)
        mongle_level = MongleLevel.objects.create(id=1)
        MongleGrade.objects.create(user=cur_user, mongle_level=mongle_level)

        cur_user_board = BoardModel.objects.create(author=cur_user, title="title", content="content")
        not_cur_user_board = BoardModel.objects.create(author=not_cur_user, title="title2", content="content2")

        BoardCommentModel.objects.create(author=cur_user, board=cur_user_board, content="content")
        BoardCommentModel.objects.create(author=not_cur_user, board=not_cur_user_board, content="content2")

    def test_get_board_list(self) -> None:
        """
        BoardView의 get 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")

        client.force_authenticate(user=user)
        url = "/board/?page_num=1"
        response = client.get(url)
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["total_count"], 2)

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
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_when_parameter_doesnot_exist_in_get_board_list(self) -> None:
        """
        BoardView의 get 함수를 검증하는 함수
        case : 빈파라미터를 넣은 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")

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
        user = UserModel.objects.get(username="ko", nickname="ko")
        request_data = {"title": "title", "content": "content", "author": user.id}

        client.force_authenticate(user=user)
        url = "/board/"
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "몽글점수를 5점 획득 하셨습니다!")

    def test_when_unauthenticated_user_in_post_board_content(self) -> None:
        """
        BoardView의 post 함수를 검증하는 함수
        case : 로그인하지 않은 사용자가 post하는 경우
        """
        client = APIClient()
        request_data = {"title": "title", "content": "content"}

        url = "/board/"
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_including_swear_word_in_board_content(self) -> None:
        """
        BoardView의 post 함수를 검증하는 함수
        case : 욕설을 포함한 내용을 post하는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        request_data = {"title": "title", "content": "바보 멍청이", "author": user.id}

        client.force_authenticate(user=user)
        url = "/board/"
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다")

    def test_exceeding_limited_num_of_char_on_post_board_title(self) -> None:
        """
        BoardView의 post 함수를 검증하는 함수
        case : 제목에 제한된 글자수(30자)를 초과하여 post하는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        request_data = {
            "title": str("a" * 40),
            "content": "content",
            "author": user.id,
        }

        client.force_authenticate(user=user)
        url = "/board/"
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드의 글자 수가 30 이하인지 확인하십시오.", result["detail"])

    def test_exceeding_limited_num_of_char_on_post_board_content(self) -> None:
        """
        BoardView의 post 함수를 검증하는 함수
        case : 내용에 제한된 글자수를 초과하여 post하는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        request_data = {
            "title": "title",
            "content": str("a" * 550),
            "author": user.id,
        }

        client.force_authenticate(user=user)
        url = "/board/"
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드의 글자 수가 500 이하인지 확인하십시오.", result["detail"])

    def test_exceeding_limited_num_of_char_on_post_board_title_and_content(self) -> None:
        """
        BoardView의 post 함수를 검증하는 함수
        case: 작성한 board의 제목과 내용이 제한 글자 수(각 30, 500자)를 초과했을 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        request_data = {
            "title": str("a" * 32),
            "content": str("a" * 550),
            "author": user.id,
        }

        client.force_authenticate(user=user)
        url = "/board/"
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드의 글자 수가 500 이하인지 확인하십시오.", result["detail"])
        self.assertIn("이 필드의 글자 수가 30 이하인지 확인하십시오.", result["detail"])

    def test_put_board_content(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(title="title", content="content", author=user)
        request_data = {"title": "수정된 제목", "content": "수정된 내용", "author": user.id}

        client.force_authenticate(user=user)
        url = "/board/" + str(user_board.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "게시글이 수정되었습니다.")

    def test_when_unauthenticated_user_put_board_content(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        case : 로그인하지 않은 사용자가 put하는 경우
        """

        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(title="title", content="content", author=user)
        request_data = {"title": "수정된 제목", "content": "수정된 내용", "author": user.id}

        url = "/board/" + str(user_board.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_when_not_author_put_board_content(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        case : 게시물을 쓴 사용자가 아닌 사람이 수정을 하려는 경우
        """

        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        not_cur_user = not_cur_user = UserModel.objects.get(username="not_cur_user", nickname="not_cur_user")
        not_cur_user_board = BoardModel.objects.get(author=not_cur_user, title="title2", content="content2")
        request_data = {"title": "수정된 제목", "content": "수정된 내용", "author": not_cur_user.id}

        client.force_authenticate(user=user)
        url = "/board/" + str(not_cur_user_board.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(result["detail"], "게시글 수정 권한이 없습니다")

    def test_when_parameter_doesnot_exist_in_put_board_list(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        case : 빈파라미터를 넣은 경우
        """

        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")

        request_data = {"title": "수정된 제목", "content": "수정된 내용", "author": user.id}

        client.force_authenticate(user=user)
        url = "/board/"

        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "게시글이 존재하지 않습니다")

    def test_including_swear_word_in_put_board_content(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        case: 수정한 내용이 욕설을 포함한 내용일 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.create(title="title", content="content", author=user)
        request_data = {"title": "수정된 제목", "content": "바보 멍청이", "author": user.id}

        client.force_authenticate(user=user)
        url = "/board/" + str(user_board.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "부적절한 내용이 담겨있어 게시글을 수정 할 수 없습니다")

    def test_exceeding_limited_num_of_char_on_put_board_title(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        case: 수정한 제목이 제한 글자 수(30자)를 초과했을 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.create(title="title", content="content", author=user)
        request_data = {
            "title": str("A" * 32),
            "content": "content",
            "author": user.id,
        }

        client.force_authenticate(user=user)
        url = "/board/" + str(user_board.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드의 글자 수가 30 이하인지 확인하십시오.", result["detail"])

    def test_exceeding_limited_num_of_char_on_put_board_content(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        case: 수정한 내용이 제한 글자 수(500자)를 초과했을 경우
        """

        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.create(title="title", content="content", author=user)
        request_data = {
            "title": "title",
            "content": str("A" * 550),
            "author": user.id,
        }

        client.force_authenticate(user=user)
        url = "/board/" + str(user_board.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드의 글자 수가 500 이하인지 확인하십시오.", result["detail"])

    def test_exceeding_limited_num_of_char_on_put_board_title_and_content(self) -> None:
        """
        BoardView의 put 함수를 검증하는 함수
        case: 수정한 제목과 내용이 제한 글자 수(각 30, 500자)를 초과했을 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.create(title="title", content="content", author=user)
        request_data = {
            "title": str("A" * 32),
            "content": str("A" * 520),
            "author": user.id,
        }

        client.force_authenticate(user=user)
        url = "/board/" + str(user_board.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드의 글자 수가 30 이하인지 확인하십시오.", result["detail"])
        self.assertIn("이 필드의 글자 수가 500 이하인지 확인하십시오.", result["detail"])

    def test_delete_board_content(self) -> None:
        """
        BoardView의 delete 함수를 검증하는 함수
        """

        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.create(title="title", content="content", author=user)
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
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.create(title="title", content="content", author=user)
        url = "/board/" + str(user_board.id)
        response = client.delete(url)
        result = response.json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_when_not_author_delete_board_content(self) -> None:
        """
        BoardView의 delete 함수를 검증하는 함수
        case: 게시물을 쓰지 않은 사람이 게시물을 삭제하려는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        not_cur_user = not_cur_user = UserModel.objects.get(username="not_cur_user", nickname="not_cur_user")
        not_cur_user_board = BoardModel.objects.get(author=not_cur_user, title="title2", content="content2")

        client.force_authenticate(user=user)
        url = "/board/" + str(not_cur_user_board.id)
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
        user = UserModel.objects.get(username="ko", nickname="ko")

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
        user = UserModel.objects.get(username="ko", nickname="ko")

        client.force_authenticate(user=user)
        url = "/board/" + str(9999)
        response = client.delete(url)
        result = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "게시글이 존재하지 않습니다")

    def test_get_board_comment_list(self) -> None:
        """
        BorderCommentView get 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")

        client.force_authenticate(user=user)
        url = "/board/comment/?board_id=1"
        response = client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_when_is_user_is_unauthenticated_in_get_board_comment_list(self) -> None:
        """
        BorderCommentView get 함수를 검증하는 함수
        case : 로그인하지 않은 사용자가 조회하는 경우
        """
        client = APIClient()

        url = "/board/comment/?board_id=1"
        response = client.get(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_when_parameter_doesnot_exist_in_get_board_comment_list(self) -> None:
        """
        BorderCommentView get 함수를 검증하는 함수
        case : 빈파라미터를 넣은 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")

        client.force_authenticate(user=user)

        with self.assertRaises(TypeError):
            get_paginated_board_data()

        url = "/board/comment/"
        response = client.get(url)
        result = response.json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "params의 board_id가 비어있습니다.")

    def test_post_board_comment_content(self) -> None:
        """
        BorderCommentView post 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.create(title="title", content="content", author=user)

        request_data = {"content": "content"}

        client.force_authenticate(user=user)
        url = "/board/comment/?board_id=" + str(user_board.id)
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "댓글이 생성되었습니다.")

    def test_when_unauthenticated_user_in_post_board_comment_content(self) -> None:
        """
        BorderCommentView post 함수를 검증하는 함수
        case : 로그인하지 않은 사용자가 post하는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.create(title="title", content="content", author=user)

        request_data = {"content": "content"}

        url = "/board/comment/?board_id=" + str(user_board.id)
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_including_swear_word_in_post_board_comment_content(self) -> None:
        """
        BorderCommentView post 함수를 검증하는 함수
        case : 욕설을 포함한 내용을 post하는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.create(title="title", content="content", author=user)

        request_data = {"content": "바보 멍청이"}

        client.force_authenticate(user=user)
        url = "/board/comment/?board_id=" + str(user_board.id)
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "부적절한 내용이 담겨있어 댓글을 작성 할 수 없습니다.")

    def test_exceeding_limited_num_of_char_on_post_board_comment_content(self) -> None:
        """
        BorderCommentView post 함수를 검증하는 함수
        case : 내용에 제한된 글자수를 초과하여 post하는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.create(title="title", content="content", author=user)

        request_data = {"content": str("A" * 520)}

        client.force_authenticate(user=user)
        url = "/board/comment/?board_id=" + str(user_board.id)
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드의 글자 수가 500 이하인지 확인하십시오.", result["detail"])

    def test_put_board_comment_content(self) -> None:
        """
        BoardCommentView의 put 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(title="title", content="content", author=user)
        user_board_comment = BoardCommentModel.objects.get(author=user, board=user_board, content="content")
        request_data = {"content": "수정된 내용"}

        client.force_authenticate(user=user)
        url = "/board/comment/" + str(user_board_comment.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "댓글이 수정되었습니다.")

    def test_when_unauthenticated_user_put_board_comment_content(self) -> None:
        """
        BoardCommentView의 put 함수를 검증하는 함수
        case : 로그인하지 않은 사용자가 put하는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(title="title", content="content", author=user)
        user_board_comment = BoardCommentModel.objects.get(author=user, board=user_board, content="content")
        request_data = {"content": "수정된 내용"}

        url = "/board/comment/" + str(user_board_comment.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_when_not_author_put_board_comment_content(self) -> None:
        """
        BoardCommentView의 put 함수를 검증하는 함수
        case : 게시물을 쓴 사용자가 아닌 사람이 수정을 하려는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        not_cur_user = not_cur_user = UserModel.objects.get(username="not_cur_user", nickname="not_cur_user")
        not_cur_user_board = BoardModel.objects.get(author=not_cur_user, title="title2", content="content2")
        not_cur_user_board_comment = BoardCommentModel.objects.get(
            author=not_cur_user, board=not_cur_user_board, content="content2"
        )
        request_data = {"content": "수정된 내용"}

        client.force_authenticate(user=user)
        url = "/board/comment/" + str(not_cur_user_board_comment.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "수정할 수 있는 권한이 없습니다.")

    def test_put_when_including_swear_word_board_comment_content(self) -> None:
        """
        BoardCommentView의 put 함수를 검증하는 함수
        case: 수정한 내용이 욕설을 포함한 내용일 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(title="title", content="content", author=user)
        user_board_comment = BoardCommentModel.objects.get(author=user, board=user_board, content="content")
        request_data = {"content": "바보 멍청이"}

        client.force_authenticate(user=user)
        url = "/board/comment/" + str(user_board_comment.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "부적절한 내용이 담겨있어 댓글을 수정 할 수 없습니다")

    def test_exceeding_limited_num_of_char_on_put_board_comment_content(self) -> None:
        """
        BoardCommentView의 put 함수를 검증하는 함수
        case: 수정한 내용이 제한 글자 수(500)를 초과했을 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(title="title", content="content", author=user)
        user_board_comment = BoardCommentModel.objects.get(author=user, board=user_board, content="content")
        request_data = {"content": str("A" * 520)}

        client.force_authenticate(user=user)
        url = "/board/comment/" + str(user_board_comment.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("이 필드의 글자 수가 500 이하인지 확인하십시오.", result["detail"])

    def test_delete_board_comment_content(self) -> None:
        """
        BoardCommentView의 delete 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(title="title", content="content", author=user)
        user_board_comment = BoardCommentModel.objects.get(author=user, board=user_board, content="content")
        client.force_authenticate(user=user)
        url = "/board/comment/" + str(user_board_comment.id)
        response = client.delete(url)
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "댓글이 삭제되었습니다.")

    def test_when_unauthenticated_user_delete_board_comment_content(self) -> None:
        """
        BoardCommentView의 delete 함수를 검증하는 함수
        case: 로그인하지 않은 사용자가 게시물을 삭제하려는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(title="title", content="content", author=user)
        user_board_comment = BoardCommentModel.objects.get(author=user, board=user_board, content="content")

        url = "/board/comment/" + str(user_board_comment.id)
        response = client.delete(url)
        result = response.json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_when_not_author_delete_board_comment_content(self) -> None:
        """
        BoardCommentView의 delete 함수를 검증하는 함수
        case: 게시물을 쓰지 않은 사람이 게시물을 삭제하려는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(title="title", content="content", author=user)
        user_board_comment = BoardCommentModel.objects.get(author=user, board=user_board, content="content")
        not_cur_user = not_cur_user = UserModel.objects.get(username="not_cur_user", nickname="not_cur_user")
        client.force_authenticate(user=not_cur_user)
        url = "/board/comment/" + str(user_board_comment.id)
        response = client.delete(url)
        result = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "댓글이 존재하지 않습니다.")

    def test_when_parameter_doesnot_exist_delete_board_comment_content(self) -> None:
        """
        BoardCommentView의 delete 함수를 검증하는 함수
        case : 빈파라미터를 넣은 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        client.force_authenticate(user=user)
        url = "/board/comment/"
        response = client.delete(url)
        result = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "댓글이 존재하지 않습니다.")

    def test_when_post_doesnot_exist_in_delete_board_comment_content(self) -> None:
        """
        BoardCommentView의 delete 함수를 검증하는 함수
        case : 존재하지 않는 게시물을 삭제하려는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        client.force_authenticate(user=user)
        url = "/board/comment/" + "9999"
        response = client.delete(url)
        result = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "댓글이 존재하지 않습니다.")

    def test_get_search_view_when_search_word_is_not_given(self) -> None:
        """
        SearchView의 get 함수를 검증
        case : 검색어가 입력되지 않았을 때
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        client.force_authenticate(user=user)
        url = "/board/search" + "?search_type=title&page_num=0"
        response = client.get(url)
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "카테고리와 검색어는 필수값입니다.")

    def test_get_search_view_when_search_data_not_found(self) -> None:
        """
        SearchView의 get 함수를 검증
        case : 검색어가 없을 때
        """
        client = APIClient()
        user = UserModel.objects.get(username="ko", nickname="ko")
        client.force_authenticate(user=user)
        url = "/board/search" + "?search_word=안녕&search_type=title&page_num=0"
        response = client.get(url)
        result = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "검색된 값이 없습니다. 다른 검색어로 다시 검색해주세요.")

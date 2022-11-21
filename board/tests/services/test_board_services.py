import os

from django.db.models import Q
from django.test import TestCase
from rest_framework import exceptions

from board.models import Board as BoardModel
from board.models import BoardComment as BoardCommentModel
from board.models import BoardLike as BoardLikeModel
from board.services.board_service import (
    check_is_it_clean_text,
    create_board_comment_data,
    create_board_data,
    delete_board_comment_data,
    delete_board_data,
    delete_like_data,
    get_board_comment_data,
    get_paginated_board_data,
    get_searched_data,
    make_like_data,
    update_board_comment_data,
    update_board_data,
)
from elasticsearch import Elasticsearch
from user.models import MongleGrade as MongleGradeModel
from user.models import MongleLevel as MongleLevelModel
from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel


class TestBoardService(TestCase):
    """
    BoardView의 service 함수를 검증하는 클래스
    """

    @classmethod
    def setUpTestData(cls):
        cur_user = UserModel.objects.create(username="ko", nickname="ko")
        UserProfileModel.objects.create(user=cur_user)
        mongle_level = MongleLevelModel.objects.create(id=1)
        MongleGradeModel.objects.create(user=cur_user, mongle_level=mongle_level)

        not_cur_user = UserModel.objects.create(username="not_cur_user", nickname="not_cur_user")
        UserProfileModel.objects.create(user=not_cur_user)
        MongleGradeModel.objects.create(user=not_cur_user, mongle_level=mongle_level)

        cur_user_board = BoardModel.objects.create(author=cur_user, title="title", content="content")
        not_cur_user_board = BoardModel.objects.create(author=not_cur_user, title="title2", content="content2")

        BoardCommentModel.objects.create(author=cur_user, board=cur_user_board, content="content")
        BoardCommentModel.objects.create(author=not_cur_user, board=not_cur_user_board, content="content2")

        elastic_client = Elasticsearch(
            f"elasticsearch://{os.environ['MONGLE_ES_HOST']}:9200",
            basic_auth=(os.environ["MONGLE_ES_USER"], os.environ["MONGLE_ES_PASSWORD"]),
        )

        if elastic_client.search(index="test", query={"match": {"title": "title"}})["hits"]["total"]["value"]:
            elastic_client.delete_by_query(index="test", query={"match": {"title": "title"}})

        elastic_client.create(
            index="test",
            id=cur_user_board.id,
            document={"title": "title", "content": "content"},
        )

    def test_check_is_it_clean_text(self):
        """
        비속어 필터링 함수 체크
        case: 비속어가 포함되어 있지 않은 경우
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        request_data = {"title": "title", "content": "봄날의 햇살", "author": user.id}
        result = check_is_it_clean_text(request_data["content"])

        self.assertTrue(result)

    def test_check_is_it_clean_text_when_contents_include_swear_word(self) -> None:
        """
        비속어 필터링 함수 체크
        case: 비속어가 포함되어 있는 경우
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        request_data = {"title": "title", "content": "바보 멍청이", "author": user.id}
        result = check_is_it_clean_text(request_data["content"])

        self.assertFalse(result)

    def test_get_paginated_board_data(self) -> None:
        """
        page_num을 통해서 board 데이터를 가져오는 service 함수 검증
        """

        author = UserModel.objects.get(username="ko", nickname="ko")
        board_query = Q()
        _, total_count = get_paginated_board_data(page_num=1, query=board_query, author=author)
        self.assertEqual(BoardModel.objects.all().count(), total_count)

    def test_get_paginated_board_data_with_unauthenticated_user(self) -> None:
        """
        page_num을 통해서 board 데이터를 가져오는 service 함수 검증
        case: 없는 페이지번호로 함수를 부를 경우
        """

        with self.assertRaises(TypeError):
            create_board_data(2)

    def test_create_board_data(self) -> None:
        """
        board 데이터를 작성하는 service 함수 검증
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        request_data = {"title": "title", "content": "content", "author": user.id}

        with self.assertNumQueries(3):
            create_board_data(request_data, user)

        board = BoardModel.objects.filter(author=user.id).last()

        self.assertEqual(3, BoardModel.objects.all().count())
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
        user = UserModel.objects.get(username="ko", nickname="ko")
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
        user = UserModel.objects.get(username="ko", nickname="ko")
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
            create_board_data(request_data, user)

    def test_update_board_data(self) -> None:
        """
        board 데이터를 업데이트 하는 service 함수 검증
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.create(title="title", content="content", author=user)
        request_data = {"title": "수정된 제목", "content": "수정된 내용", "author": user.id}

        with self.assertNumQueries(3):
            update_board_data(user_board.id, request_data, user)

        updated_board = BoardModel.objects.get(id=user_board.id)

        self.assertEqual(updated_board.title, "수정된 제목")
        self.assertEqual(updated_board.content, "수정된 내용")

    def test_update_board_data_with_unauthenticated_user(self) -> None:
        """
        board 데이터를 업데이트 하는 service 함수 검증
        case: 로그인 하지 않은 사용자가 put(수정)하는 경우
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(author=user, title="title", content="content")
        request_data = {"title": "수정된 제목", "content": "수정된 내용", "author": user.id}

        with self.assertRaises(exceptions.PermissionDenied):
            update_board_data(user_board.id, request_data, None)

    def test_update_board_data_which_doesnot_exist(self) -> None:
        """
        board 데이터를 업데이트 하는 service 함수 검증
        case: 없는 게시글을 수정하려고 할 때
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        request_data = {"title": "수정된 제목", "content": "수정된 내용", "author": user.id}

        with self.assertRaises(BoardModel.DoesNotExist):
            update_board_data(None, request_data, user.id)

    def test_update_board_data_by_not_author(self) -> None:
        """
        board 데이터를 업데이트 하는 service 함수 검증
        case: 게시물을 쓴 사용자가 아닌 사람이 수정을 하려는 경우
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        not_cur_user = UserModel.objects.get(username="not_cur_user", nickname="not_cur_user")
        user_board = BoardModel.objects.create(title="title", content="content", author=user)
        request_data = {"title": "수정된 제목", "content": "수정된 내용", "author": not_cur_user.id}

        with self.assertRaises(exceptions.PermissionDenied):
            update_board_data(user_board.id, request_data, user.id)

    def test_update_board_data_when_title_with_over_limited_num(self) -> None:
        """
        board 데이터를 업데이트 하는 service 함수 검증
        case: 제목이 제한 글자수 이상인 경우
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(author=user, title="title", content="content")
        request_data = {
            "title": "30자 이상입니다. 30자 이상입니다. 30자 이상입니다",
            "content": "content",
            "author": user.id,
        }
        with self.assertRaises(exceptions.ValidationError):
            update_board_data(user_board.id, request_data, user)

    def test_update_board_data_when_content_with_over_limited_num(self) -> None:
        """
        board 데이터를 업데이트 하는 service 함수 검증
        case: 내용이 제한 글자수 이상인 경우
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(author=user, title="title", content="content")
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
            update_board_data(user_board.id, request_data, user)

    def test_delete_board_data(self) -> None:
        """
        board 데이터를 삭제하는 service 함수 검증
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(author=user, title="title", content="content")

        self.assertEqual(2, BoardModel.objects.all().count())

        with self.assertNumQueries(7):
            delete_board_data(user_board.id, user)

        self.assertEqual(1, BoardModel.objects.all().count())

    def test_delete_board_data_with_unauthenticated_user(self) -> None:
        """
        board 데이터를 삭제하는 service 함수 검증
        case : 로그인 하지 않은 사용자가 삭제하려는 경우
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(author=user, title="title", content="content")
        with self.assertRaises(exceptions.PermissionDenied):
            delete_board_data(user_board.id, None)

    def test_delete_board_data_which_doesnot_exist(self) -> None:
        """
        board 데이터를 삭제하는 service 함수 검증
        case: 없는 게시글을 삭제하려고 할 때
        """
        user = UserModel.objects.get(username="ko", nickname="ko")

        with self.assertRaises(BoardModel.DoesNotExist):
            delete_board_data(None, user.id)

    def test_delete_board_data_by_not_author(self) -> None:
        """
        board 데이터를 삭제하는 service 함수 검증
        case: 게시물을 쓴 사용자가 아닌 사람이 삭제 하려는 경우
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        not_cur_user = UserModel.objects.get(username="not_cur_user", nickname="not_cur_user")
        user_board = BoardModel.objects.get(author=user, title="title", content="content")
        with self.assertRaises(exceptions.PermissionDenied):
            delete_board_data(user_board.id, not_cur_user.id)

    def test_get_board_comment_data(self) -> None:
        """
        board_comment 데이터를 불러오는 service에 대한 검증
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(content="content")

        self.assertEqual("content", get_board_comment_data(user_board.id, author=user)[0]["content"])

    def test_create_board_comment_data(self) -> None:
        """
        해당 board의 comment 데이터를 작성하는 service 함수 검증
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(author=user)
        request_data = {"content": "content"}

        with self.assertNumQueries(2):
            create_board_comment_data(user, user_board.id, request_data)

        self.assertEqual(2, BoardModel.objects.all().count())
        self.assertEqual(user_board.boardcomment_set.all().last().content, "content")

    def test_create_board_comment_data_when_title_with_over_limited_num(self) -> None:
        """
        해당 board의 comment 데이터를 작성하는 service 함수 검증
        case: 작성한 제목이 제한 글자수(500자) 이상인 경우
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(author=user)
        request_data = {"content": str("a" * 600)}
        with self.assertRaises(exceptions.ValidationError):
            create_board_comment_data(user, user_board.id, request_data)

    def test_update_board_comment_data(self) -> None:
        """
        해당 board_comment 데이터를 업데이트 하는 service 함수 검증
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(author=user, title="title", content="content")
        user_board_comment = BoardCommentModel.objects.get(author=user, board=user_board, content="content")
        request_data = {"content": "수정된 내용"}

        with self.assertNumQueries(2):
            update_board_comment_data(request_data, user_board_comment.id)

        updated_board_comment = BoardCommentModel.objects.get(author=user)

        self.assertEqual(updated_board_comment.content, "수정된 내용")

    def test_update_board_comment_data_which_doesnot_exist(self) -> None:
        """
        해당 board_comment 데이터를 업데이트 하는 service 함수 검증
        case: 없는 댓글을 수정하려고 할 때
        """

        request_data = {"content": "수정된 내용"}

        with self.assertRaises(BoardCommentModel.DoesNotExist):
            update_board_comment_data(request_data, 9999)

    def test_update_board_comment_data_when_title_with_over_limited_num(self) -> None:
        """
        해당 board_comment 데이터를 업데이트 하는 service 함수 검증
        case: 내용이 제한 글자수 이상인 경우
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(author=user, title="title", content="content")
        user_board_comment = BoardCommentModel.objects.get(author=user, board=user_board, content="content")
        request_data = {"content": str("a" * 550)}

        with self.assertRaises(exceptions.ValidationError):
            update_board_comment_data(request_data, user_board_comment.id)

    def test_delete_board_comment_data(self) -> None:
        """
        board_comment 데이터를 삭제하는 service 함수 검증
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(author=user, title="title", content="content")
        user_board_comment = BoardCommentModel.objects.get(author=user, board=user_board, content="content")

        self.assertEqual(2, BoardCommentModel.objects.all().count())

        with self.assertNumQueries(3):
            delete_board_comment_data(user_board_comment.id, user)

        self.assertEqual(1, BoardCommentModel.objects.all().count())

    def test_delete_board_comment_data_which_doesnot_exist(self) -> None:
        """
        board_comment 데이터를 삭제하는 service 함수 검증
        case: 없는 board_comment를 삭제하려고 할 때
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        with self.assertRaises(BoardCommentModel.DoesNotExist):
            delete_board_comment_data(9999, user)

        self.assertEqual(2, BoardCommentModel.objects.all().count())

    def test_make_like_data(self) -> None:
        """
        board에 like 데이터를 만드는 service함수 검증
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(author=user, title="title", content="content")
        with self.assertNumQueries(2):
            make_like_data(author=user, board_id=user_board.id)

        self.assertEqual(1, BoardLikeModel.objects.all().count())

    def test_when_none_board_make_like_data(self) -> None:
        """
        board에 like 데이터를 만드는 service함수 검증
        case : 없는 board에 like를 눌렀을 경우
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        with self.assertRaises(BoardModel.DoesNotExist):
            make_like_data(author=user, board_id=9999)

        self.assertEqual(0, BoardLikeModel.objects.all().count())

    def test_delete_like_data(self) -> None:
        """
        board에 like 데이터를 삭제하는 service함수 검증
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        user_board = BoardModel.objects.get(author=user, title="title", content="content")
        make_like_data(author=user, board_id=user_board.id)
        with self.assertNumQueries(3):
            delete_like_data(author=user, board_id=user_board.id)

        self.assertEqual(0, BoardLikeModel.objects.all().count())

    def test_get_paginated_data_with_search_query_happy_case(self) -> None:
        """ """
        user = UserModel.objects.get(username="ko", nickname="ko")
        searched_board_ids, total_count = get_searched_data(
            search_word="title", search_type="title", search_index="test", page_num=0
        )

        query_for_search = Q(id__in=searched_board_ids)

        paginated_boards, _ = get_paginated_board_data(query=query_for_search, author=user, page_num=1)

        self.assertEqual(1, len(paginated_boards))
        self.assertEqual(1, total_count)

    def test_get_paginated_data_with_search_query_when_data_not_exist(self) -> None:
        """
        검색된 데이터의 board를 가져오는 함수
        case : 데이터가 없을 때
        """
        with self.assertRaises(IndexError):
            get_searched_data(search_word="타이틀", search_type="title", search_index="test", page_num=0)

    def test_get_searched_data_when_search_word_is_not_given(self) -> None:
        """
        엘라스틱 서치에 데이터를 검색하는 함수 검증
        case: 검색어를 입력하지 않았을 때
        """
        with self.assertRaises(ValueError):
            get_searched_data(search_word="", search_type="title", search_index="test", page_num=0)

    def test_get_searched_data_when_search_type_is_not_given(self) -> None:
        """
        엘라스틱 서치에 데이터를 검색하는 함수 검증
        case: 검색어 타입이 빈 값일 때
        """
        with self.assertRaises(ValueError):
            get_searched_data(search_word="title", search_type="", search_index="test", page_num=0)

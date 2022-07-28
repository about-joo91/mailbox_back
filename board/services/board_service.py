from typing import Dict, List, Tuple
from rest_framework import exceptions

import unsmile_filtering
from board.models import Board as BoardModel
from board.models import BoardComment as BoardCommentModel
from board.models import BoardLike as BoardLikeModel
from board.serializers import BoardCommentSerializer, BoardSerializer


def check_is_it_clean_text(check_content):
    """
    작성하는 데이터에 욕설이 있는지 검증하는 service
    """
    filtering_sys = unsmile_filtering.post_filtering
    result = filtering_sys.unsmile_filter(check_content)
    if result["label"] == "clean":
        return True
    return False


def get_paginated_board_data(page_num: int) -> Tuple[List, int]:
    """
    page_num을 통해서 board 데이터를 가져오는 service
    """
    paginated_board = BoardModel.objects.all().order_by("-create_date")[
        10 * (page_num - 1) : 10 + 10 * (page_num - 1)
    ]
    total_count = BoardModel.objects.count()
    return paginated_board, total_count


def create_board_data(board_data: Dict, author_id: int) -> None:
    """
    board 데이터를 작성하는 service
    """
    board_data["author"] = author_id
    create_board_serializer = BoardSerializer(data=board_data)
    if create_board_serializer.is_valid():
        create_board_serializer.save()
        return "저장"
    return create_board_serializer.errors



def update_board_data(board_id : int , update_data : Dict, user_id:int) -> None:
    """
    board 데이터를 업데이트 하는 service
    """
    update_board = BoardModel.objects.get(id=board_id)
    if user_id != update_board.author.id:
        raise exceptions.PermissionDenied
    update_board_serializer = BoardSerializer(
        update_board, data=update_data, partial=True
    )
    update_board_serializer.is_valid(raise_exception=True)
    update_board_serializer.save()


def delete_board_data(board_id: int, author_id: int) -> None:
    """
    board 데이터를 삭제하는 service
    """
    delete_model = BoardModel.objects.get(id=board_id)
    if author_id != delete_model.author.id:
        raise exceptions.PermissionDenied
    delete_model.delete()


def make_like_data(author: int, board_id: int) -> None:
    """
    like 데이터를 만드는 service
    """
    target_board = BoardModel.objects.get(id=board_id)
    like_board = BoardLikeModel.objects.create(author=author, board=target_board)


def delete_like_data(author: int, board_id: int) -> None:
    """
    like 데이터를 삭제하는 service
    """
    target_board = BoardModel.objects.get(id=board_id)
    liked_board = BoardLikeModel.objects.get(author=author, board=target_board)
    liked_board.delete()


def get_board_comment_data(board_id: int) -> List:
    """
    해당 board의 comment 데이터의 댓글을 불러오는 service
    """
    board_comment = BoardModel.objects.filter(id=board_id)
    return board_comment


def create_board_comment_data(author: str, board_id: int, create_data: Dict) -> None:
    """
    해당 board의 comment 데이터를 만드는 service
    """
    create_data["author"] = author.id
    create_data["board"] = board_id
    create_board_comment_serializer = BoardCommentSerializer(data=create_data)
    create_board_comment_serializer.is_valid(raise_exception=True)
    create_board_comment_serializer.save()


def update_board_comment_data(update_data: Dict, comment_id: int) -> None:
    """
    해당 board의 comment 데이터를 수정하는 service
    """
    update_comment = BoardCommentModel.objects.get(id=comment_id)
    update_comment_serializer = BoardCommentSerializer(
        update_comment, data=update_data, partial=True
    )
    update_comment_serializer.is_valid(raise_exception=True)
    update_comment_serializer.save()


def delete_board_comment_data(comment_id: int, author_id: int) -> None:
    """
    해당 board의 comment 데이터를 삭제하는 service
    """
    delete_comment = BoardCommentModel.objects.get(id=comment_id, author=author_id)
    delete_comment.delete()

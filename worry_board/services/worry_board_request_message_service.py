from typing import Dict, List, Tuple

from user.models import User as UserModel
from worry_board.models import RequestMessage as RequestMessageModel
from worry_board.models import RequestStatus as RequestStatusModel
from worry_board.models import WorryBoard as WorryBoardModel
from worry_board.serializers import DetailRequestMessageSerializer, RequestMessageSerializer


def get_paginated_request_message_data(page_num: int, case: str, author: UserModel) -> Tuple[List, int]:
    """
    request_data를 가져오는 service
    """
    if case == "sended":
        paginated_request_message = (
            RequestMessageModel.objects.select_related("worry_board__category")
            .filter(author=author)
            .order_by("-create_date")[10 * (page_num - 1) : 10 + 10 * (page_num - 1)]
        )
    elif case == "received":
        paginated_request_message = RequestMessageModel.objects.filter(worry_board__author=author).order_by(
            "-create_date"
        )[10 * (page_num - 1) : 10 + 10 * (page_num - 1)]
    paginated_request_messages = RequestMessageSerializer(
        paginated_request_message, many=True, context={"author": author}
    ).data
    total_count = paginated_request_message.count()
    return paginated_request_messages, total_count


def create_request_message_data(author: UserModel, worry_board_id: int, request_message: Dict[str, str]):
    """
    request_message를 만드는 service
    """
    get_request_message = RequestMessageModel.objects.filter(author=author, worry_board_id=worry_board_id).exists()
    if get_request_message is False:
        worry_board = WorryBoardModel.objects.get(id=worry_board_id)
        request_status = RequestStatusModel.objects.get(status="요청취소")
        request_message_serializer = RequestMessageSerializer(data=request_message)
        request_message_serializer.is_valid(raise_exception=True)
        request_message_serializer.save(
            author_id=author.id, worry_board_id=worry_board.id, request_status_id=request_status.id
        )


def update_request_message_data(for_update_data: Dict[str, str], request_message_id: int) -> None:
    """
    request_message를 수정하는 service
    """
    update_request_message = RequestMessageModel.objects.get(id=request_message_id)
    update_request_message_serializer = RequestMessageSerializer(
        update_request_message, data=for_update_data, partial=True
    )
    update_request_message_serializer.is_valid(raise_exception=True)
    update_request_message_serializer.save()


def delete_request_message_data(request_message_id: int):
    """
    request_message를 삭제하는 service
    """
    delete_request_message = RequestMessageModel.objects.get(id=request_message_id)

    if delete_request_message:
        delete_request_message.delete()


def accept_request_message_data(request_message_id: int) -> None:
    """
    기존의 request_message를 수정하여
    받은 request_message를 수락하는 service
    """
    accept_request_message = RequestMessageModel.objects.get(id=request_message_id)
    request_status = RequestStatusModel.objects.get(status="수락됨")
    for_update_data = {"can_write_letter": True}
    update_request_message_serializer = RequestMessageSerializer(
        accept_request_message, data=for_update_data, partial=True
    )
    update_request_message_serializer.is_valid(raise_exception=True)
    update_request_message_serializer.save(request_status_id=request_status.id)


def disaccept_request_message_data(request_message_id: int) -> None:
    """
    기존의 request_message를 수정하여
    받은 request_message를 거절하는 service
    """
    accept_request_message = RequestMessageModel.objects.get(id=request_message_id)
    request_status = RequestStatusModel.objects.get(status="반려됨")
    for_update_data = {"can_write_letter": False}
    update_request_message_serializer = RequestMessageSerializer(
        accept_request_message, data=for_update_data, partial=True
    )
    update_request_message_serializer.is_valid(raise_exception=True)
    update_request_message_serializer.save(request_status_id=request_status.id)


def update_request_status(author: UserModel, worry_board_id):
    """
    편지작성을 완료 후 reqeust_status를 작성 완료로 변경하는 service
    """
    worry_board = WorryBoardModel.objects.get(id=worry_board_id)
    request_message = worry_board.requestmessage_set.filter(author=author)
    request_message.update(request_status=5)


def post_detail_message(author: UserModel, request_message_id: int, request_data: Dict[str, str]):
    """
    요청 수락 시 detail_message를 작성하는 service
    """
    detail_request_message_serializer = DetailRequestMessageSerializer(data=request_data)
    detail_request_message_serializer.is_valid(raise_exception=True)
    detail_request_message_serializer.save(author_id=author.id, request_message_id=request_message_id)

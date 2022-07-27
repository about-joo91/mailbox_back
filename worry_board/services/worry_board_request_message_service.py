from typing import Dict, List, Tuple

from worry_board.models import RequestMessage as RequestMessageModel
from worry_board.serializers import RequestMessageSerializer


def get_paginated_request_message_data(page_num : int, case : str, author : str) -> Tuple[List , int]:
    """
    request_data를 가져오는 service
    """
    if case == "sended":
        paginated_request_message = RequestMessageModel.objects.filter(author = author).order_by("-create_date")[
            10 * (page_num - 1) : 10 + 10 * (page_num - 1)
        ]
    elif case == "recieve":
        paginated_request_message = RequestMessageModel.objects.filter(worry_board__author=author).order_by("-create_date")[
            10 * (page_num - 1) : 10 + 10 * (page_num - 1)
        ]
    total_count = paginated_request_message.count()
    return paginated_request_message, total_count

def create_request_message_data(author : str, worry_board_id : int, request_message : str):
    """
    request_message를 만드는 service
    """
    get_request_message = RequestMessageModel.objects.filter(author=author, worry_board_id=worry_board_id).exists()
    if get_request_message == False:
        RequestMessageModel.objects.create(
            author = author,
            worry_board_id = worry_board_id,
            request_message = request_message
        )

def update_request_message_data(for_updata_date : Dict, request_message_id : int) -> None:
    """
    request_message를 수정하는 service
    """
    update_request_message = RequestMessageModel.objects.get(id=request_message_id)
    update_request_message_serializer = RequestMessageSerializer(
        update_request_message, data=for_updata_date, partial=True
    )
    update_request_message_serializer.is_valid(raise_exception=True)
    update_request_message_serializer.save()

def delete_request_message_data(request_message_id : int):
    """
    request_message를 삭제하는 service
    """
    delete_request_message = RequestMessageModel.objects.get(id=request_message_id)
    if delete_request_message:
        delete_request_message.delete()

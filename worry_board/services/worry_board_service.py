from typing import Dict, List, Tuple

import unsmile_filtering
from worry_board.models import RequestMessage as RequestMessageModel
from worry_board.models import WorryBoard as WorryBoardModel
from worry_board.serializers import RequestMessageSerializer, WorryBoardSerializer


def get_paginated_worry_board_data(page_num: int, category: int) -> Tuple[List, int]:
    """
    worry_board의 데이터를 가져오는 service
    """
    if category == 0:
        paginated_worry_board = WorryBoardModel.objects.all().order_by("-create_date")[
            10 * (page_num - 1) : 10 + 10 * (page_num - 1)
        ]
        total_count = WorryBoardModel.objects.count()
    else:
        paginated_worry_board = WorryBoardModel.objects.filter(category=category).order_by("-create_date")[
            10 * (page_num - 1) : 10 + 10 * (page_num - 1)
        ]
        total_count = WorryBoardModel.objects.filter(category=category).count()

    return paginated_worry_board, total_count


def create_worry_board_data(create_data: Dict, author: str) -> None:
    """
    worry_board의 데이터를 만드는 service
    """
    create_data["author"] = author.id
    create_worry_board_serializer = WorryBoardSerializer(data=create_data)
    create_worry_board_serializer.is_valid(raise_exception=True)
    create_worry_board_serializer.save()


def check_is_it_clean_text(check_content):
    """
    작성하는 데이터에 욕설이 있는지 검증하는 service
    """
    filtering_sys = unsmile_filtering.post_filtering
    result = filtering_sys.unsmile_filter(check_content)
    if result["label"] == "clean":
        return True
    return False


def update_worry_board_data(worry_board_id: int, update_worry_board_data: Dict) -> None:
    """
    worry_board 데이터를 업데이트 하는 service
    """
    update_worry_board = WorryBoardModel.objects.filter(id=worry_board_id)
    update_worry_board_serializer = WorryBoardSerializer(update_worry_board, data=update_worry_board_data, partial=True)
    update_worry_board_serializer.is_valid(raise_exception=True)
    update_worry_board_serializer.save()


def delete_worry_board_data(worry_board_id: int, author: str) -> None:
    """
    worry_board 데이터를 삭제하는 service
    """
    delete_model = WorryBoardModel.objects.get(id=worry_board_id, author=author.id)
    delete_model.delete()


def get_paginated_request_message_data(page_num: int, case: str, author: str) -> Tuple[List, int]:
    """
    request_data를 가져오는 service
    """
    if case == "sended":
        paginated_request_message = RequestMessageModel.objects.filter(author=author).order_by("-create_date")[
            10 * (page_num - 1) : 10 + 10 * (page_num - 1)
        ]
    elif case == "recieve":
        paginated_request_message = RequestMessageModel.objects.filter(worry_board__author=author).order_by(
            "-create_date"
        )[10 * (page_num - 1) : 10 + 10 * (page_num - 1)]
    total_count = paginated_request_message.count()
    return paginated_request_message, total_count


def create_request_message_data(author: str, worry_board_id: int, request_message: str):
    """
    request_message를 만드는 service
    """
    get_request_message = RequestMessageModel.objects.filter(author=author, worry_board_id=worry_board_id).exists()
    if get_request_message == False:
        RequestMessageModel.objects.create(
            author=author,
            worry_board_id=worry_board_id,
            request_message=request_message,
        )


def update_request_message_data(for_updata_date: Dict, request_message_id: int) -> None:
    """
    request_message를 수정하는 service
    """
    update_request_message = RequestMessageModel.objects.get(id=request_message_id)
    update_request_message_serializer = RequestMessageSerializer(
        update_request_message, data=for_updata_date, partial=True
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

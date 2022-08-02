from typing import Dict, List, Tuple

import unsmile_filtering
from user.models import User as UserModel
from worry_board.models import WorryBoard as WorryBoardModel
from worry_board.serializers import WorryBoardSerializer


def get_paginated_worry_board_data(
    page_num: int, category: int, recommended_worryboard: list = []
) -> Tuple[List, int, List]:
    """
    worry_board의 데이터를 가져오는 service
    """
    if category == 0:
        paginated_worry_board = WorryBoardModel.objects.all().order_by("-create_date")[
            10 * (page_num - 1) : 10 + 10 * (page_num - 1)
        ]
        total_count = WorryBoardModel.objects.count()

    elif category == 7:
        paginated_worry_board = recommended_worryboard[10 * (page_num - 1) : 10 + 10 * (page_num - 1)]
        total_count = recommended_worryboard.count()

    else:
        paginated_worry_board = WorryBoardModel.objects.filter(category=category).order_by("-create_date")[
            10 * (page_num - 1) : 10 + 10 * (page_num - 1)
        ]
        total_count = WorryBoardModel.objects.filter(category=category).count()

    return paginated_worry_board, total_count


def create_worry_board_data(author: UserModel, create_data: Dict[str, str]) -> None:
    """
    worry_board의 데이터를 만드는 service
    """
    create_worry_board_serializer = WorryBoardSerializer(data=create_data)
    create_worry_board_serializer.is_valid(raise_exception=True)
    create_worry_board_serializer.save(author=author)


def update_worry_board_data(worry_board_id: int, update_data: Dict[str, str]) -> None:
    """
    worry_board 데이터를 업데이트 하는 service
    """
    update_worry_board = WorryBoardModel.objects.get(id=worry_board_id)
    update_worry_board_serializer = WorryBoardSerializer(update_worry_board, data=update_data, partial=True)
    update_worry_board_serializer.is_valid(raise_exception=True)
    update_worry_board_serializer.save()


def delete_worry_board_data(author: UserModel, worry_board_id: int) -> None:
    """
    worry_board 데이터를 삭제하는 service
    """
    delete_model = WorryBoardModel.objects.get(author_id=author.id, id=worry_board_id)
    delete_model.delete()


def check_is_it_clean_text(check_content: str) -> bool:
    """
    작성하는 데이터에 욕설이 있는지 검증하는 service
    """
    filtering_sys = unsmile_filtering.post_filtering
    result = filtering_sys.unsmile_filter(check_content)
    if result["label"] == "clean":
        return True
    return False

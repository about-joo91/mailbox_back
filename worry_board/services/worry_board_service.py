from typing import Dict, List, Tuple

import unsmile_filtering
from worry_board.models import WorryBoard as WorryBoardModel
from worry_board.serializers import WorryBoardSerializer

def get_worry_board_data(page_num : int, category : int) -> Tuple[List, int]:
    if category == 0:
        worry_board_list = WorryBoardModel.objects.all().order_by("-create_date")[
                10 * (page_num - 1) : 10 + 10 * (page_num - 1)
            ]
        total_count = WorryBoardModel.objects.count()
    else:
        worry_board_list = WorryBoardModel.objects.filter(
            category=category
        ).order_by("-create_date")[10 * (page_num - 1) : 10 + 10 * (page_num - 1)]
        total_count = WorryBoardModel.objects.filter(category=category).count()

    return worry_board_list, total_count


def create_worry_board_data(geted_data : Dict, author_id : int) -> None:
    geted_data["author"] = author_id
    create_worry_board_serializer = WorryBoardSerializer(data=geted_data)
    create_worry_board_serializer.is_valid(raise_exception=True)
    create_worry_board_serializer.save()

def test_is_it_clean_text(test_data):
    filtering_sys = unsmile_filtering.post_filtering
    result = filtering_sys.unsmile_filter(test_data["content"])
    if result["label"] == "clean":
        return True
    return False

def update_worry_board_data(worry_board_id : int , update_worry_board_data : Dict) -> None:
    """
    worry_board 데이터를 업데이트 하는 service
    """
    update_worry_board = WorryBoardModel.objects.get(id=worry_board_id)
    update_worry_board_serializer = WorryBoardSerializer(
        update_worry_board, data=update_worry_board_data, partial=True
    )
    update_worry_board_serializer.is_valid(raise_exception=True)
    update_worry_board_serializer.save()

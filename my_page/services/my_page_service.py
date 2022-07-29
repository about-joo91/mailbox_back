from django.db.models import Q

from main_page.models import Letter as LetterModel
from my_page.serializers import LetterSerializer


def get_letter_data_by_user(query: Q, letter_num: int) -> dict[str, str]:
    return LetterSerializer(
        LetterModel.objects.select_related("letter_author__userprofile")
        .select_related("letter_author__monglegrade")
        .select_related("worryboard__author__userprofile")
        .select_related("worryboard__author__monglegrade")
        .select_related("worryboard__category")
        .filter(query)[letter_num]
    ).data


def get_not_read_letter_count(query: Q) -> int:
    return LetterModel.objects.filter(query).count()

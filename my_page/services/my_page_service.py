from django.db.models import Q

from main_page.models import Letter as LetterModel
from my_page.serializers import LetterSerializer


def get_letter_data_by_user(query: Q, letter_num: int) -> dict[str, str]:
    if LetterModel.objects.filter(query).exists():
        letter_model_by_user = LetterSerializer(
            LetterModel.objects.select_related("letter_author__userprofile")
            .select_related("letter_author__monglegrade")
            .select_related("letter_author__monglegrade__mongle_level")
            .select_related("worryboard__author__userprofile")
            .select_related("worryboard__author__monglegrade")
            .select_related("worryboard__author__monglegrade__mongle_level")
            .select_related("worryboard__category")
            .select_related("letterreview")
            .filter(query)[letter_num]
        ).data
        return letter_model_by_user
    raise LetterModel.DoesNotExist


def get_not_read_letter_count(query: Q) -> int:
    return LetterModel.objects.filter(query).count()

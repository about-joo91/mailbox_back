from typing import Dict

from django.db.models import Q

from jin.models import Letter as LetterModel
from my_page.serializers import LetterSerializer


def get_letter_data_by_user(query: Q, letter_num: int) -> Dict:
    return LetterSerializer(
        LetterModel.objects.select_related("worryboard__category").filter(query)[
            letter_num
        ]
    ).data

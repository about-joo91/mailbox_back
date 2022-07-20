from django.db.models import Q

from jin.models import Letter as LetterModel


def get_letter_data_by_user(query: Q, letter_num: int) -> LetterModel:
    return LetterModel.objects.select_related("worryboard__category").filter(query)[
        letter_num
    ]

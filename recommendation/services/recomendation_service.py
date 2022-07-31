from django.http import HttpResponse

from main_page.models import Letter as LetterModel
from recommendation import recommender


def recommend_worryboard_list(cur_user: object):
    """
    추천시스템 service
    """
    try:
        latest_user_letter = LetterModel.objects.filter(letter_author=cur_user).order_by("-create_date").first()
        worryboard_id_of_letter = latest_user_letter.worryboard.id
        recomendation_sys = recommender.recommend_worryboard
        final_worryboard_list = recomendation_sys.recommend_worries(worryboard_id_of_letter, cur_user)
        return final_worryboard_list

    except AttributeError:
        return HttpResponse(status=204)

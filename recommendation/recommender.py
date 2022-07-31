import random
from django.db.models.query_utils import Q
from django.http import HttpResponse

import pandas as pd

from worry_board.models import WorryBoard as WorryBoardModel
from main_page.models import Letter as LetterModel




class Recommendation:
    def __init__(self):
        self.worry_data = pd.read_csv("worryboard.csv")
        self.cos = pd.read_csv("cosine_sim.csv")
        
        # worryboard 아이디로 코사인 데이터프레임의 인덱스 구하기
        self.id_to_index = dict(zip(self.worry_data["id"], self.worry_data.index))
        # 데이터프레임 인덱스로 worryboard 아이디 구하기
        self.index_to_id = dict(zip(self.worry_data.index, self.worry_data["id"]))

    def recommend_worries(self, latest_worryboard_id, cur_user):
        try:
            # 해당 워리보드의 코사인 유사도 내림차순 정렬
            recommend_index = list(
                self.cos.loc[self.id_to_index[latest_worryboard_id]].sort_values(ascending=False).index
            )
            recommend_ids = [self.index_to_id[int(index)] for index in recommend_index]
            
            final_worryboard_list = WorryBoardModel.objects.filter(Q(id__in = recommend_ids)).exclude(
                Q(id__in = LetterModel.objects.values_list('worryboard_id', flat=True))|Q(author=cur_user))[:3]
            
            return final_worryboard_list

        except KeyError:
            return HttpResponse(status=204)


recommend_worryboard = Recommendation()

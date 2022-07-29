import random

import pandas as pd

from worry_board.models import WorryBoard as WorryBoardModel


class Recommendation:
    def __init__(self):
        self.worry_data = pd.read_csv("worryboard.csv")
        self.cos = pd.read_csv("cosine_sim.csv")

        # worryboard 아이디로 코사인 데이터프레임의 인덱스 구하기
        self.id_to_index = dict(zip(self.worry_data["id"], self.worry_data.index))
        # 데이터프레임 인덱스로 worryboard 아이디 구하기
        self.index_to_id = dict(zip(self.worry_data.index, self.worry_data["id"]))

    def recommend_worries(self, latest_worryboard_id):
        try:
            recommend_index = list(
                self.cos.loc[self.id_to_index[latest_worryboard_id]].sort_values(ascending=False)[:4].index
            )
            recommend_ids = [self.index_to_id[int(index)] for index in recommend_index]
            recommend_ids.remove(latest_worryboard_id)

            result_obj = []
            for worryboard_id in recommend_ids:
                result = WorryBoardModel.objects.get(id=worryboard_id)
                result_obj.append(result)

            return result_obj

        except KeyError:
            result_obj = list(WorryBoardModel.objects.all())
            # change 3 to how many random items you want
            random_items = random.sample(result_obj, 3)
            print(random_items)
            return random_items


recommend_worryboard = Recommendation()

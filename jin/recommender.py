# import pandas as pd
# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity

# from jin.models import LetterReviewLike as LetterReviewLikeModel
# from jin.models import LetterReview as LetterReviewModel
# from jin.models import Letter as LetterModel
# from worry_board.models import WorryBoard as WorryBoardModel


# class Recommendation:
#     def __init__(self):
#         # 좋아요한 레터리뷰
#         letter_review_like = pd.DataFrame(LetterReviewLikeModel.objects.all().values())
#         letter_review = pd.DataFrame(LetterReviewModel.objects.all().values())
#         letter = pd.DataFrame(LetterModel.objects.all().values())

#         userlike_board = pd.merge(letter_review_like, letter_review, left_on='review_id_id', right_on ="id")
#         userlike_board_2 = pd.merge(userlike_board, letter, left_on='letter_id', right_on ="id")
#         userlike_board_2["like"] = 1

#         # 필요한 데이터 머지
#         self.result_0 = userlike_board_2[["user_id_id", "review_id_id", "letter_id", "grade", "category_id", "worryboard_id", "like"]]
#         print(self.result_0)

#         # 피벗테이블 만들기
#         result_1_pivot = self.result_0.pivot_table('like', index='user_id_id', columns='review_id_id')
#         result_1_pivot = result_1_pivot.fillna(0)
#         self.result_1_pivot = pd.DataFrame(result_1_pivot)
#         print(self.result_1_pivot)

#         # 코사인 유사도 구하기
#         result_2_cos = cosine_similarity(result_1_pivot,result_1_pivot)
#         self.result_2_cos = pd.DataFrame(result_2_cos, index=result_1_pivot.index, columns=result_1_pivot.index)
#         print(self.result_2_cos)

#     def recommend_worries(self, user_id):
#         try:
#             # 유저 아이디 넣고 가장 비슷한 유저 한명
#             similar_user = self.result_2_cos[user_id].sort_values(ascending=False).sort_values(ascending=False)[:2].index[1]
#             print(similar_user)

#             # 가장 비슷한 유저가 좋아하는 리뷰레터 아이디로 워리보드 아이디 구하기
#             reviewletter_ids = self.result_1_pivot.loc[similar_user].sort_values(ascending=False)
#             print(reviewletter_ids.index)

#             worryboard_obj = []
#             for i in list(reviewletter_ids.index):
#                 print(i)
#                 if reviewletter_ids[i] == 1.0:
#                     worry_board_id = self.result_0[self.result_0["review_id_id"] == i].worryboard_id.values[0]
#                     print(worry_board_id)
#                     result = WorryBoardModel.objects.get(id=worry_board_id)
#                     worryboard_obj.append(result)
#                     print(worryboard_obj)
#                 else:
#                     break
#             print(worryboard_obj)
#             return worryboard_obj


#         except KeyError:
#             print("keyerror!")
#             return


# recommend_worryboard = Recommendation()

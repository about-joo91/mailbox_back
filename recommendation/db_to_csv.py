# from flask import Flask, render_template, request, jsonify, send_file
# import os
# import pymysql
# import csv
# import pandas as pd
# import re

# app = Flask(__name__)

# conn = pymysql.connect(
#         host='database-1.c4vg7kihi1fg.ap-northeast-2.rds.amazonaws.com',
#         user='admin',
#         password='loveyourself',
#         db='mail_box',
#         charset="utf8",
#         autocommit=True,
#         cursorclass=pymysql.cursors.DictCursor,
#     )

# # Konlpy 라이브러리
# from konlpy.tag import Okt
# okt = Okt()

# # 벡터화하는 식
# from sklearn.feature_extraction.text import TfidfVectorizer
# tf = TfidfVectorizer(analyzer='word', ngram_range=(1,1), min_df = 1)



# @app.route('/test', methods=['GET'])
# def test_get():
    
#     try:
#         with conn.cursor() as cursor:
#             data = []
#             sql ="SELECT `worry_board_worryboard`.`id`, `worry_board_worryboard`.`author_id`, `worry_board_worryboard`.`category_id`, `worry_board_worryboard`.`content`, `worry_board_worryboard`.`create_date` FROM `worry_board_worryboard` WHERE NOT (`worry_board_worryboard`.`id` IN (SELECT U0.`worryboard_id` FROM `main_page_letter` U0 WHERE U0.`worryboard_id` IS NOT NULL))"
#             cursor.execute(sql)
#             rows = cursor.fetchall()
#             for row in rows:
#                 data.append(row)
#     finally:
#         cursor.close()
#         conn.close()
#     print(data)

#     headers = ["id", "content", "author_id", "category_id","create_date"]
#     rows = data

#     with open("worryboard.csv", "w") as f:
#         f_csv = csv.DictWriter(f, fieldnames=headers)
#         f_csv.writeheader()
#         f_csv.writerows(rows)
        
#     # worryboard_data = pd.read_csv("worryboard.csv")
    
#     # worryboard_data["like"] = 1
    
#     # result_1_pivot = worryboard_data.pivot_table('like', index='user_id_id', columns='review_id_id')
    
#     making_cosine_data()
#     return send_file("worryboard.csv")





# def making_cosine_data():
#     try:
#         with conn.cursor() as cursor:
#             # data = []
#             sql ="SELECT * FROM `worry_board_worryboard`"
#             cursor.execute(sql)
#             # rows = cursor.fetchall()
#             # for row in rows:
#             #     data.append(row)
#             result = cursor.fetchall()
            
#             total_worryboard = pd.DataFrame(result)

            
#             goal_list = []
#             for k in range(len(total_worryboard['content'])): 
#                 goal = re.sub(r'[^\s\w]', ' ', total_worryboard['content'][k]) # cleaning
#                 goal = re.sub('\s+', ' ', goal) # 한줄로 
#                 goal_list.append(goal)   
#             total_worryboard['content_cleaning'] = goal_list
            
#             # 함수 결과 새로운 'result' 컬럼에 붙이기
#             result = []
#             for i in range(len(total_worryboard['content_cleaning'])):
#                 a = pos_filtering(total_worryboard['content_cleaning'][i])
#                 result.append(a)
#             total_worryboard['result'] = result
            
#             total_worryboard['result'] = total_worryboard['result'].apply(lambda x : (' ').join(x))
            
#             # 벡터화
#             tfidf_matrix = tf.fit_transform(total_worryboard['result'].values.astype('U'))
#             tfidf_matrix
            
#             # 코사인유사도 구하기
#             from sklearn.metrics.pairwise import cosine_similarity
#             cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
#             cosine_sim = pd.DataFrame(cosine_sim)
            
#             cosine_sim.to_csv("cosine_sim.csv", index = False)
            
            
#     finally:
#         cursor.close()
#         conn.close()
#     print(data)

#     headers = ["id", "content", "author_id", "category_id","create_date"]
#     rows = data

#     with open("worryboard.csv", "w") as f:
#         f_csv = csv.DictWriter(f, fieldnames=headers)
#         f_csv.writeheader()
#         f_csv.writerows(rows)



# # 줄거리에서 명사만 필터링하는 함수
# def pos_filtering(text): 
#     pos_word_list = okt.pos(text, stem = True) # 토크나이징 / 스테밍
#     pos_list = ['Noun']
#     pos_filtered_word_list = []

#     for word, pos in pos_word_list: # 품사 필터링
#         if pos in pos_list:
#             pos_filtered_word_list.append(word)
#     return pos_filtered_word_list
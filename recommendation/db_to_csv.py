
# from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
# import os
# import pymysql
# import csv
# import pandas as pd
# import re
# from konlpy.tag import Okt
# from sklearn.feature_extraction.text import TfidfVectorizer
# import zipfile

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
# okt = Okt()

# # 벡터화하는 식
# tf = TfidfVectorizer(analyzer='word', ngram_range=(1,1), min_df = 1)



# @app.route('/test', methods=['GET'])
# def test_get():

#     try:
#         with conn.cursor() as cursor:
#             data = []
#             sql ="SELECT * FROM `worry_board_worryboard`"
#             cursor.execute(sql)
#             rows = cursor.fetchall()
#             for row in rows:
#                 data.append(row)
#     except:
#         cursor.close()
#         conn.close()
#     print(data)

#     # worryboard.csv 만들기
#     headers = ["id", "content", "author_id", "category_id","create_date"]
#     rows = data
    
#     with open("worryboard.csv", "w") as f:
#         f_csv = csv.DictWriter(f, fieldnames=headers)
#         f_csv.writeheader()
#         f_csv.writerows(rows)

#     # 코사인 유사도 데이터 만들기
#     making_cosine_data()

#     # 두 csv 파일 압축해 리턴
#     file_list = ['worryboard.csv', 'cosine_sim.csv']

#     with zipfile.ZipFile("recommendation_system.zip", 'w') as my_zip:
#         for i in file_list:
#             my_zip.write(i)
#         my_zip.close()

#     return send_file("recommendation_system.zip")


# def making_cosine_data():
#     with conn.cursor() as cursor:
#         sql ="SELECT * FROM `worry_board_worryboard`"
#         cursor.execute(sql)
#         result = cursor.fetchall()

#         total_worryboard = pd.DataFrame(result)

#         goal_list = []
#         for k in range(len(total_worryboard['content'])):
#             goal = re.sub(r'[^\s\w]', ' ', total_worryboard['content'][k]) # cleaning
#             goal = re.sub('\s+', ' ', goal) # 한줄로
#             goal_list.append(goal)
#         total_worryboard['content_cleaning'] = goal_list

#         # 함수 결과 새로운 'result' 컬럼에 붙이기
#         result = []
#         for i in range(len(total_worryboard['content_cleaning'])):
#             a = pos_filtering(total_worryboard['content_cleaning'][i])
#             result.append(a)
#         total_worryboard['result'] = result

#         total_worryboard['result'] = total_worryboard['result'].apply(lambda x : (' ').join(x))

#         # 벡터화
#         tfidf_matrix = tf.fit_transform(total_worryboard['result'].values.astype('U'))
#         tfidf_matrix

#         # 코사인유사도 구하기
#         from sklearn.metrics.pairwise import cosine_similarity
#         cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
#         cosine_sim = pd.DataFrame(cosine_sim)
#         print(cosine_sim)

#         cosine_sim.to_csv("cosine_sim.csv", index = False)



# # 줄거리에서 명사만 필터링하는 함수
# def pos_filtering(text):
#     pos_word_list = okt.pos(text, stem = True) # 토크나이징 / 스테밍
#     pos_list = ['Noun']
#     pos_filtered_word_list = []

#     for word, pos in pos_word_list: # 품사 필터링
#         if pos in pos_list:
#             pos_filtered_word_list.append(word)
#     return pos_filtered_word_list




# if __name__ == '__main__':
#    app.run('0.0.0.0',port=5002,debug=True)


import csv
import os

import pymysql

# csv 파일로 만들기
conn = pymysql.connect(
    host=os.environ["RDS_HOST"],
    user=os.environ["RDS_USER"],
    password=os.environ["RDS_PASSWORD"],
    db=os.environ["RDS_DB_NAME"],
    charset="utf8",
    autocommit=True,
    cursorclass=pymysql.cursors.DictCursor,
)

try:
    with conn.cursor() as cursor:
        data = []
        sql = "select * from worry_board_worryboard"
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            data.append(row)
finally:
    cursor.close()
    conn.close()
print(data)

headers = ["id", "content", "create_date", "author_id", "category_id"]
rows = data

with open("worryboard.csv", "w") as f:
    f_csv = csv.DictWriter(f, fieldnames=headers)
    f_csv.writeheader()
    f_csv.writerows(rows)


# import pandas as pd
# import numpy as np
# # import matplotlib.pyplot as plt
# # import seaborn as sns
# from ast import literal_eval
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.metrics.pairwise import cosine_similarity, linear_kernel

# from worry_board.models import WorryBoard as WorryBoardModel
# from jin.models import Letter as LetterModel

# # 사용자가 쓴 편지, 워리보드 가져오기
# user_letter = LetterModel.objects.all()
# print(user_letter)

# # 그 컨텐츠 분석
# # Mecab
# from konlpy.tag import Mecab
# m = Mecab()
# m.nouns('오늘은 텍스트마이닝 마지막 스터디입니다.')

# # Okt
# from konlpy.tag import Okt
# okt = Okt() # Twitter의 이름이 Okt로 변경됨

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

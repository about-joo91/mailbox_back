import time

import requests
import schedule

# def test():
#     print("나는 바보가 아니다")
#     # POST (JSON)

#     # csv 파일로 만들기
#     conn = pymysql.connect(
#         host=os.environ["RDS_HOST"],
#         user=os.environ["RDS_USER"],
#         password=os.environ["RDS_PASSWORD"],
#         db=os.environ["RDS_DB_NAME"],
#         charset="utf8",
#         autocommit=True,
#         cursorclass=pymysql.cursors.DictCursor,
#     )

#     print(conn)

#     try:
#         with conn.cursor() as cursor:
#             data = []
#             sql = "select id, content, author_id, category_id from worry_board_worryboard"
#             cursor.execute(sql)
#             rows = cursor.fetchall()
#             for row in rows:
#                 data.append(row)
#     finally:
#         cursor.close()
#         conn.close()
#     print(data)

#     headers = {'Content-Type': 'application/json; chearset=utf-8'}
#     datas = {'data': data}
#     res = requests.post('http://127.0.0.1:5002/test', data=json.dumps(datas), headers=headers)
#     print(str(res.status_code) + " | " + res.text)


def test():
    res = requests.get("http://54.180.75.68:5002/test")
    save_file = open("worryboard.csv", "wb")
    save_file.write(res.content)
    save_file.close()
    print(str(res.status_code))
    print("성공!")


# 5초에 한번씩 함수 실행
schedule.every(5).seconds.do(test)

# 2시간에 한번씩 함수 실행
# schedule.every(2).hour.do(test)
# 3일에 한번씩 함수 실행
# schedule.every(3).days.do(test)

# 매일 13시 30분에 함수 실행
# schedule.every().day.at("13:30").do(test)
# 매일 "11:11:11"에 함수 실행
# schedule.every().day.at("11:11:11").do(test)


while True:
    schedule.run_pending()
    time.sleep(1)

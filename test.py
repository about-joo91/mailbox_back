import time

import requests
import schedule


def test():
    res = requests.get("http://54.180.75.68:5002/test")
    save_file = open("worryboard.csv", "wb")
    save_file.write(res.content)
    save_file.close()
    print(str(res.status_code))
    print("성공!")


# 5초에 한번씩 함수 실행
schedule.every(5).seconds.do(test)

# # 2시간에 한번씩 함수 실행
# # schedule.every(2).hour.do(test)
# # 3일에 한번씩 함수 실행
# # schedule.every(3).days.do(test)

# # 매일 13시 30분에 함수 실행
# schedule.every().day.at("10:58").do(test)
# # 매일 "11:11:11"에 함수 실행
# # schedule.every().day.at("11:11:11").do(test)


while True:
    schedule.run_pending()
    time.sleep(1)

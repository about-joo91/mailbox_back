import requests


# Create your views here.
def db_to_csv():
    res = requests.get("http://54.180.75.68:5002/test")
    save_file = open("worryboard.csv", "wb")
    save_file.write(res.content)
    save_file.close()
    print(str(res.status_code), "성공!")

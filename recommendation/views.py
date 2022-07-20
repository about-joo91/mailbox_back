import requests

# from django.shortcuts import render

# Create your views here.


def test():
    res = requests.get("http://54.180.75.68:5002/test")
    save_file = open("worryboard.csv", "wb")
    save_file.write(res.content)
    save_file.close()
    print(str(res.status_code))
    print("성공!")

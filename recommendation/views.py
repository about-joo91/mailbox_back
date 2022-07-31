import requests
import zipfile
import io
import pandas as pd


# Create your views here.
def db_to_csv():
    res = requests.get("http://54.180.75.68:5002/test")
    res.raise_for_status()
    zfile = zipfile.ZipFile(io.BytesIO(res.content))
    zfile.extractall()
    print(str(res.status_code), "성공!")

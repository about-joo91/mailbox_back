import io
import zipfile

import requests


# Create your views here.
def db_to_csv():
    res = requests.get("http://3.34.97.111:8000/recommendation")
    res.raise_for_status()
    zfile = zipfile.ZipFile(io.BytesIO(res.content))
    zfile.extractall()

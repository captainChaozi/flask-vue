import random
import string
import time
import pandas as pd
import hashlib


def md5(string):
    m = hashlib.md5()
    m.update(string.encode("utf-8"))
    return m.hexdigest()

def generate_unique(size=20):
    return ''.join([random.choice(string.ascii_letters) for _ in range(size)])


def get_file_name(suffix):
    return str(int(time.time()))[5:] + generate_unique(5) + '.' + suffix


def excel_json(file,sheet=0):
    df = pd.read_excel(file,sheet_name=sheet)
    # print(df)
    return df.to_dict('records')

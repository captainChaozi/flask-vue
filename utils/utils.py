import string
import random
from uuid import uuid1


def generate_unique(size=20):
    return ''.join([random.choice(string.ascii_letters) for _ in range(size)])


def generate_id():
    return str(uuid1()).replace('-','')

import binascii
import hashlib
import hmac
import json
import os
from base64 import urlsafe_b64encode
from datetime import datetime
from utils.tools.json_encoder import CJsonEncoder


def random_value():
    return binascii.b2a_base64(os.urandom(24))[:-1]


def _encode_json(obj):
    return bytearray(json.dumps(obj, separators=(',', ':'), cls=CJsonEncoder), 'utf-8')


def _encode_token(claims):
    encoded_claims = _encode_json(claims)
    return hmac.new(random_value(), encoded_claims, hashlib.sha256).digest()


def create_token(data):
    data['timestamp'] = datetime.now()
    token = _encode_token(data)
    return urlsafe_b64encode(token).decode()

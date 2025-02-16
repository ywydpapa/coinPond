import jwt
import hashlib
import os
import requests
import uuid
from urllib.parse import urlencode, unquote
import dbconn
import dotenv



uno = 100001
getkey = dbconn.getupbitkey_tr(uno)
access_key = getkey[0]
secret_key = getkey[1]
server_url = "https://api.upbit.com"

payload = {
    'access_key': access_key,
    'nonce': str(uuid.uuid4()),
}

jwt_token = jwt.encode(payload, secret_key)
authorization = 'Bearer {}'.format(jwt_token)
headers = {
  'Authorization': authorization,
}


def getwallet():
    global res
    try:
        res = requests.get(server_url + '/v1/accounts', headers=headers)
        for item in res.json():
            print(item)
    except Exception as e:
        print(e)
    finally:
        return res.json()

getwallet()
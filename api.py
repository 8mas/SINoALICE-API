import hashlib
import random
import time
import requests
import secrets
import hmac
import json
import msgpack
import crypto
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES


class API:
    debug = True
    instances = 0
    URL = "https://api-sinoalice-us.pokelabo.jp/api/login"

    def __init__(self):
        self.request_session = requests.session()
        self.request_session.verify = False

        # Use local proxy
        if API.debug:
            print("Using proxy")
            self.request_session.proxies.update({"http": "http://127.0.0.1:8888", "https": "https://127.0.0.1:8888", })

    def _generate_hmac(self, request_type, resource, timestamp, data: str):

        return ""

    # Set headers for request
    def _prepare_request(self, request_type, resource, data):
        return ""

    def _handle_response(self, response):
        response_dict = json.loads(response.content.decode())
        code = response.status_code

        return response_dict

    def _get(self, resource, params={}):
        url = API.URL + resource

        self._prepare_request("GET", resource, {})
        response = self.request_session.get(url, params=params)
        return self._handle_response(response)

    def _post(self, resource, payload: str):
        url = API.URL + resource

        self._prepare_request("POST", resource, payload)
        response = self.request_session.post(url, payload)
        return self._handle_response(response)

    def _put(self):
        pass

    def _delete(self):
        pass

    ########## Helper ##########
    # a bit sloppy but okay for now


class SigningException(Exception):
    pass

if __name__ == "__main__":
    with open("get_user_data.msg", "rb") as data_file:
        byte_data = data_file.read()
    crypt = crypto.RijndaelEncryptor()
    key = b"***REMOVED***"
    aes = AES.new(key, AES.MODE_CBC, byte_data[0:16])
    pad_text = aes.decrypt(byte_data[16:])
    print(pad_text[:-2])
    text = unpad(pad_text, 128)
    data_loaded = msgpack.unpackb(pad_text[:-2])
    print(data_loaded)

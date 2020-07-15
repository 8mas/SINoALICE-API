import requests
import json
import msgpack
from Crypto.Hash.SHA1 import SHA1Hash
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA1, MD5, SHA256
from Crypto.PublicKey import RSA

import hmac
import base64
import time
import random
from collections import OrderedDict
from urllib.parse import quote_plus

DEBUG = True
instances = 0


def encodeRFC3986(input_string):
    if input_string is None:
        return input_string
    sb = ""
    for c in input_string:
        if (c < 'A' or c > 'Z') and ((c < 'a' or c > 'z') and not ((c >= '0' and c <= '9') or c == '-' or c == '.' or c == '_' or c == '~')):
            for b in c.encode():
                sb += "%".join('%02x'.format() % b)
        else:
            sb += c
    return sb


def generate_nonce(length=19):
    return hex(int(''.join([str(random.randint(0, 15)) for i in range(length)])))


class API:
    URL = "https://api-sinoalice-us.pokelabo.jp"
    crypto_key = b"***REMOVED***"
    app_secret = "***REMOVED***"
    def __init__(self):
        self.request_session = requests.session()
        self.request_session.verify = False

        self.consumer_key = generate_nonce(15)  # Like device id
        self.private_key = RSA.generate(1024)

        # Use local proxy
        if DEBUG:
            print("Using proxy")
            self.request_session.proxies.update({"http": "http://127.0.0.1:8888", "https": "https://127.0.0.1:8888", })

    """
    Benutzung von SHA1-RSA-PKCS 
    DefaultSigner wird für den ersten kontakt genommen
    Dann Authoratife für den zweiten (auth/x_uid)
    
    """

    def register_new_account(self):
        oauth_header = self._build_oauth_header()

        pass

    def login(self):
        pass

    def _build_oauth_header(self, rest_method: str, full_url: str, body_data: bytes, new_account=False):
        oauth_header = {
            "oauth_body_hash": f"{base64.b64encode(SHA1.new(body_data).digest()).decode()}",
            "oauth_consumer_key": f"{self.consumer_key}",
            "oauth_nonce": f"{-6646833009595137866}",
            "oauth_signature_method": f"{'HMAC-SHA1' if new_account else 'RSA-SHA1'}",
            "oauth_timestamp": f"{int(time.time())}",
            "oauth_version": "1.0"
        }

        auth_string = ""
        for key, value in sorted(oauth_header.items()):
            if key == "oauth_signature":
                continue
            auth_string += quote_plus(key)
            auth_string += "="
            auth_string += quote_plus(value)
            auth_string += "&"

        string_to_hash = quote_plus(rest_method) + "&" + \
                      quote_plus(full_url) + "&" + \
                      quote_plus(auth_string.rsplit("&", 1)[0])

        if new_account:
            oauth_signature = hmac.new("TODO_get_this.secret", string_to_hash, "SHA1")
        else:
            hashed_string = SHA1.new(string_to_hash.encode())
            oauth_signature = pkcs1_15.new(self.private_key).sign(hashed_string)

        oauth_header["oauth_signature"] = base64.b64encode(oauth_signature)

        oauth_header_entry = "Oauth "
        for key, value in sorted(oauth_header.items()):
            oauth_header_entry += key
            oauth_header_entry += "=\""
            oauth_header_entry += quote_plus(value)
            oauth_header_entry += "\","
        oauth_header_entry = oauth_header_entry[:-1]
        print(oauth_header_entry)

    def _generate_signatur(self, data: bytes):
        mac = SHA1.new(data).digest()
        return mac

    def _decrypt_response(self, response_content: bytes) -> dict:
        iv = response_content[0:16]
        aes = AES.new(self.crypto_key, AES.MODE_CBC, iv)
        pad_text = aes.decrypt(response_content[16:])
        text = unpad(pad_text, 16)
        data_loaded = msgpack.unpackb(text)
        return data_loaded

    def _encrypt_request(self, request_content: bytes):
        request_content = pad(request_content, 16)
        iv = request_content[0:16]  # TODO check if ok
        aes = AES.new(self.crypto_key, AES.MODE_CBC, iv)
        text = aes.encrypt(request_content)
        data_loaded = msgpack.packb(text)
        return iv + data_loaded

    def _prepare_request(self, request_type, resource, data, remove_header=None):
        data = self._encrypt_request(data.encode())
        mac = self._generate_signatur(data)

        exit(1)
        common_headers = {
            "Host": "api-sinoalice-us.pokelabo.jp",
            "User-Agent": "UnityRequest com.nexon.sinoalice 1.0.16 (OnePlus ONEPLUS A6000 Android OS 10 / API-29 (QKQ1.190716.003/2002220019))",
            "X-Unity-Version": "2018.4.19f1",
            "Content-Type": "application/json",
            "Expect": "100-continue",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": "TODO_Define",
            "X-post-signature": f"{mac}"
        }
        for header in remove_header:
            common_headers.pop(header)

        self.request_session.headers = common_headers

    def _handle_response(self, response):
        decrypted_response = self._decrypt_response(response.content)
        code = response.status_code
        print(decrypted_response)
        return decrypted_response

    def _get(self, resource, params={}):
        url = API.URL + resource

        self._prepare_request("GET", resource, {})
        response = self.request_session.get(url, params=params)
        return self._handle_response(response)

    def _post(self, resource, payload: str, remove_header=None):
        url = API.URL + resource

        self._prepare_request("POST", resource, payload, remove_header=remove_header)

        response = self.request_session.post(url, payload)
        return self._handle_response(response)

    def _put(self):
        pass

    def _delete(self):
        pass

    ########## API ##########
    # a bit sloppy but okay for now

    def POST__api_login(self):
        payload = {
            "payload": {
                "appVersion": "1.0.16",
                "urlParam": None,
                "deviceModel": "OnePlus ONEPLUS A6000",
                "osType": 2,
                "osVersion": "Android OS 10 / API-29 (QKQ1.190716.003/2002220019)",
                "storeType": 2,
                "graphicsDeviceId": 0,
                "graphicsDeviceVendorId": 0,
                "processorCount": 8,
                "processorType": "ARM64 FP ASIMD AES",
                "supportedRenderTargetCount": 8,
                "supports3DTextures": True,
                "supportsAccelerometer": True,
                "supportsComputeShaders": True,
                "supportsGyroscope": True,
                "supportsImageEffects": True,
                "supportsInstancing": True,
                "supportsLocationService": True,
                "supportsRenderTextures": True,
                "supportsRenderToCubemap": True,
                "supportsShadows": True,
                "supportsSparseTextures": True,
                "supportsStencil": 1,
                "supportsVibration": True,
                "uuid": None,  # TODO check
                "xuid": 928750150,  # TODO check
                "locale": "en_US",
                "numericCountryCode": 826  # TODO check
            },
            "uuid": "***REMOVED***636a36e2c5f747fdb12e059a5f830369",  # Todo generate
            "userId": 0,
            "sessionId": "",
            "actionToken": None,
            "ctag": None,
            "actionTime": 132381034208143910
        }

        payload = json.dumps(payload)
        self._post("/api/login", payload, remove_header={'Cookie'})


class SigningException(Exception):
    pass

"""
Hooked
POST&https%3A%2F%2Fbn-payment-us.wrightflyer.net%2Fv1.0%2Fauth%2Fauthorize&oauth_body_hash%3D2jmj7l5rSw0yVb%252FvlWAYkK%252FYBwk%253D%26oauth_consumer_key%3D0x181d2de911f99bdcd83%26oauth_nonce%3D-6646833009595137866%26oauth_signature_method%3DRSA-SHA1%26oauth_timestamp%3D1594837849%26oauth_version%3D1.0

Nonce -6646833009595137866
GenerateSignaturString
GET&https%3A%2F%2Fbn-moderation-us.wrightflyer.net%2Fv1.0%2Fmoderate%2Fkeywordlist&oauth_body_hash%3D2jmj7l5rSw0yVb%252FvlWAYkK%252FYBwk%253D%26oauth_consumer_key%3D***REMOVED***%26oauth_nonce%3Dcaa48ee35fb3907ba1d6637887fbe794%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D1594822363%26oauth_version%3D1.0%26timestamp%3D1594637669 ***REMOVED***"""
if __name__ == "__main__":
    a = API()
    a._build_oauth_header("POST", "https://bn-payment-us.wrightflyer.net/v1.0/auth/authorize", b"")
    #a.POST__api_login()

    n = "9038718546081284029"
    print(SHA1.new("***REMOVED***".encode()).hexdigest())

import requests
import json
import msgpack
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES

DEBUG = True
instances = 0

class API:
    URL = "https://api-sinoalice-us.pokelabo.jp"
    key = b"***REMOVED***"

    def __init__(self):
        self.request_session = requests.session()
        self.request_session.verify = False

        # Use local proxy
        if DEBUG:
            print("Using proxy")
            self.request_session.proxies.update({"http": "http://127.0.0.1:8888", "https": "https://127.0.0.1:8888", })

    def _generate_hmac(self, request_type, resource, timestamp, data: str):

        return ""

    def _decrypt_response(self, response_content: bytes) -> dict:
        aes = AES.new(self.key, AES.MODE_CBC, response_content[0:16])
        pad_text = aes.decrypt(response_content[16:])
        text = unpad(pad_text, 16)
        data_loaded = msgpack.unpackb(text)
        return data_loaded

    def _encrypt_request(self, request_content: bytes):
        pass

    # Set headers for request
    def _prepare_request(self, request_type, resource, data, remove_headers=None):

        # Headers
        common_headers = {
            "Host": "api-sinoalice-us.pokelabo.jp",
            "User-Agent": "UnityRequest com.nexon.sinoalice 1.0.16 (OnePlus ONEPLUS A6000 Android OS 10 / API-29 (QKQ1.190716.003/2002220019))",
            "X-Unity-Version": "2018.4.19f1",
            "Content-Type": "application/json",
            "Expect": "100-continue",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": "TODO_Define",
            "Content-Length": "TODO_Define",
            "X-post-signature": "TODO_Define"
        }

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

    def _post(self, resource, payload: str, remove_header=None):
        url = API.URL + resource

        self._prepare_request("POST", resource, payload)
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
            "uuid": None, # TODO check
            "xuid": 928750150, # TODO check
            "locale": "en_US",
            "numericCountryCode": 826 # TODO check
        },
        "uuid": "***REMOVED***636a36e2c5f747fdb12e059a5f830369", # Todo generate
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

if __name__ == "__main__":
    a = API()
    a.POST__api_login()
import requests
import json
import msgpack
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA

import hmac
import base64
import time
import random
from urllib.parse import quote_plus

from DeviceInformation import DeviceInfo
from PlayerInformation import PlayerInformation

DEBUG = True


def generate_nonce(length=19):
    return int(''.join([str(random.randint(0, 9)) for i in range(length)]))


class BaseApi:
    URL = "https://api-sinoalice-us.pokelabo.jp"
    BN_PAYMENT_URL = "https://bn-payment-us.wrightflyer.net"
    BN_MODERATION_URL = "https://bn-moderation-us.wrightflyer.net"

    crypto_key = b"***REMOVED***"  # Reverse: Static, Unity part, BasicCrypto.encrypt
    app_secret_payment = "***REMOVED***"  # Reverse: Static, Java Part, .sign.AuthorizedSigner constructor
    app_secret_moderation = "***REMOVED***"
    app_id = "***REMOVED***"  # Reverse: Static, web log

    def __init__(self, player_information: PlayerInformation = None):
        self.request_session = requests.session()
        self.request_session.verify = False

        self.player_information = player_information
        if player_information is None:
            self.player_information = PlayerInformation()

        self.device_info = DeviceInfo()
        self.session_id: str = ""

        # Use local proxy
        if DEBUG:
            print("Using proxy")
            self.request_session.proxies.update({"http": "http://127.0.0.1:8888", "https": "https://127.0.0.1:8888", })

    # We can not fake a attestation :/ we can leave it empty or throw an error that is defined in the app
    def _payment_device_verification(self):
        nonce = "/v1.0/deviceverification/nonce"
        authorization = self._build_oauth_header_entry("POST", self.BN_PAYMENT_URL + nonce, b"", self.app_secret_payment,
                                                       self.player_information.private_key_payment)

        header = self.device_info.get_bn_payment_header(authorization)
        self.request_session.headers = header
        self.request_session.post(self.BN_PAYMENT_URL + nonce)


        verify_endpoint = "/v1.0/deviceverification/verify"
        verification_payload = {
            "device_id": f"{self.player_information.device_id}",
            "compromised": False,
            "emulator": False,
            "debug": False,
            "installer": "com.android.vending",
            "bundle_id": "com.nexon.sinoalice",
            "app_version": "1.5.0",
            "os_version": "10",
            "sf_jws": ""
        }

        payload = json.dumps(verification_payload).encode()
        authorization = self._build_oauth_header_entry("POST", self.BN_PAYMENT_URL + verify_endpoint, payload,
                                                       self.app_secret_payment, self.player_information.private_key_payment)

        header = self.device_info.get_bn_payment_header(authorization)
        self.request_session.headers = header
        self.request_session.post(self.BN_PAYMENT_URL + verify_endpoint, payload)

    def _payment_authorize(self):
        authorize_endpoint = "/v1.0/auth/authorize"

        authorization = self._build_oauth_header_entry("POST", self.BN_PAYMENT_URL + authorize_endpoint, b"",
                                                       self.app_secret_payment, self.player_information.private_key_payment)

        header = self.device_info.get_bn_payment_header(authorization)
        self.request_session.headers = header
        self.request_session.post(self.BN_PAYMENT_URL + authorize_endpoint)

    def _payment_registration(self):
        auth_initialize = "/v1.0/auth/initialize"

        device_info_dict = self.device_info.get_device_info_dict()
        device_info_dict["uuid"] = None
        device_info_dict["xuid"] = 0

        login_payload = {
            "device_id": f"{self.player_information.device_id}",
            "token": f"{self.player_information.private_key_payment.publickey().export_key().decode()}",
            "payload": json.dumps(device_info_dict)
        }

        login_payload_bytes = json.dumps(login_payload).encode()
        authorization = self._build_oauth_header_entry("POST", self.BN_PAYMENT_URL + auth_initialize,
                                                       login_payload_bytes, self.app_secret_payment, new_account=True)

        header = self.device_info.get_bn_payment_header(authorization)
        header["Authorization"] = authorization
        self.request_session.headers = header

        response = self.request_session.post(self.BN_PAYMENT_URL + auth_initialize, login_payload_bytes)
        self.uuid_payment = response.json()["uuid"]


        auth_x_uid = "/v1.0/auth/x_uid"
        authorization = self._build_oauth_header_entry("GET", self.BN_PAYMENT_URL + auth_x_uid, b"",
                                                       self.app_secret_payment, self.player_information.private_key_payment)

        header["Authorization"] = authorization
        response = self.request_session.get(self.BN_PAYMENT_URL + auth_x_uid)
        self.x_uid_payment = response.json()["x_uid"]

    def _moderation_registration(self):
        auth_initialize = "/v1.0/auth/initialize"

        device_info_dict = self.device_info.get_device_info_dict()
        device_info_dict["uuid"] = self.uuid_payment
        device_info_dict["xuid"] = 0

        login_payload = {
            "device_id": f"{self.player_information.device_id}",
            "token": f"{self.player_information.private_key_moderation.publickey().export_key().decode()}",
            "payload": json.dumps(device_info_dict)
        }

        login_payload_bytes = json.dumps(login_payload)
        authorization = self._build_oauth_header_entry("POST", self.BN_MODERATION_URL + auth_initialize,
                                                       login_payload_bytes.encode(), self.app_secret_moderation, new_account=True)

        header = self.device_info.get_bn_moderation_header(authorization)

        self.request_session.headers = header
        response = self.request_session.post(self.BN_MODERATION_URL + auth_initialize, login_payload_bytes)
        self.uuid_moderation = response.json()["uuid"]

    def _login_account(self):
        inner_payload = self.device_info.get_device_info_dict()
        inner_payload["uuid"] = None
        inner_payload["xuid"] = self.x_uid_payment

        payload = {
            "payload": inner_payload,
            "uuid": self.uuid_payment,
            "userId": 0,
            "sessionId": "",
            "actionToken": None,
            "ctag": None,
            "actionTime": 132381034208143910 # TODO
        }

        self._post("/api/login", payload, remove_header={'Cookie'})

    def login(self, new_registration=False):
        if new_registration:
            self._payment_registration()
            self._moderation_registration()
            self._login_account()
        else:
            pass
        self._payment_device_verification()
        self._payment_authorize()

    def _build_oauth_header_entry(self, rest_method: str, full_url: str, body_data: bytes, app_secret, rsa_key=None,
                                  new_account=False):
        timestamp = int(time.time())
        oauth_header = {
            "oauth_body_hash": f"{base64.b64encode(SHA1.new(body_data).digest()).decode()}",
            "oauth_consumer_key": f"{self.app_id}",
            "oauth_nonce": f"{generate_nonce()}",
            "oauth_signature_method": f"{'HMAC-SHA1' if new_account else 'RSA-SHA1'}",
            "oauth_timestamp": f"{timestamp}",
            "oauth_version": "1.0"
        }

        if not new_account:
            to_hash = (app_secret + str(timestamp)).encode()
            param_signature = self._generate_signature(to_hash, SHA1, rsa_key)
            oauth_header["xoauth_as_hash"] = param_signature.strip()
            oauth_header["xoauth_requestor_id"] = self.uuid_payment

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
            oauth_signature = hmac.new(app_secret.encode(), string_to_hash.encode(), "SHA1").digest()
            oauth_signature = base64.b64encode(oauth_signature)
        else:
            oauth_signature = self._generate_signature(string_to_hash.encode(), SHA1, rsa_key)

        oauth_header["oauth_signature"] = oauth_signature

        oauth_header_entry = "OAuth "
        for key, value in sorted(oauth_header.items()):
            oauth_header_entry += key
            oauth_header_entry += "=\""
            oauth_header_entry += quote_plus(value)
            oauth_header_entry += "\","
        oauth_header_entry = oauth_header_entry[:-1]
        return oauth_header_entry

    def _generate_signature(self, data: bytes, hash_function, key):
        hashed_string = hash_function.new(data)
        signature = pkcs1_15.new(key).sign(hashed_string)
        return base64.b64encode(signature)

    def _decrypt_response(self, response_content: bytes) -> dict:
        iv = response_content[0:16]
        aes = AES.new(self.crypto_key, AES.MODE_CBC, iv)
        pad_text = aes.decrypt(response_content[16:])
        text = unpad(pad_text, 16)
        data_loaded = msgpack.unpackb(text)
        return data_loaded

    def _encrypt_request(self, request_content: dict):
        packed_request_content = msgpack.packb(request_content)
        iv = packed_request_content[0:16]
        padded_request_content = pad(packed_request_content, 16)
        aes = AES.new(self.crypto_key, AES.MODE_CBC, iv)
        encrypted_request_content = aes.encrypt(padded_request_content)
        return iv + encrypted_request_content

    def _prepare_request(self, request_type, resource, data: dict, remove_header=None):
        data = self._encrypt_request(data)
        mac = self._generate_signature(data, SHA1, self.player_information.private_key_payment).decode()

        common_headers = {
            "Expect": "100-continue",
            "User-Agent": f"UnityRequest com.nexon.sinoalice {self.device_info.appVersion} ({self.device_info.deviceModel}"
                          f" Android OS 10 / API-29)",
            "X-post-signature": f"{mac}",
            "X-Unity-Version": "2018.4.19f1",
            "Content-Type": "application/x-msgpack",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": "TODO_Define",
            "Host": "api-sinoalice-us.pokelabo.jp",

        }
        for header in remove_header:
            common_headers.pop(header)

        self.request_session.headers = common_headers
        return data

    def _handle_response(self, response):
        decrypted_response = self._decrypt_response(response.content)
        code = response.status_code
        return decrypted_response

    def _get(self, resource, params={}):
        url = BaseApi.URL + resource

        self._prepare_request("GET", resource, {})
        response = self.request_session.get(url, params=params)
        return self._handle_response(response)

    def _post(self, resource, payload: dict, remove_header=None):
        url = BaseApi.URL + resource

        payload = self._prepare_request("POST", resource, payload, remove_header=remove_header)

        response = self.request_session.post(url, payload)
        return self._handle_response(response)

    def _put(self):
        pass

    def _delete(self):
        pass


class SigningException(Exception):
    pass

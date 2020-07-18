from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA1
from urllib.parse import quote_plus
from sqlalchemy.orm import sessionmaker, session
from Crypto.PublicKey import RSA

import requests
import logging
import json
import msgpack
import hmac
import base64
import time
import datetime
import random

from DeviceInformation import DeviceInfo
from PlayerInformation import PlayerInformation

requests.packages.urllib3.disable_warnings()
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

DEBUG = True


def generate_nonce(length=19):
    return int(''.join([str(random.randint(0, 9)) for i in range(length)]))


def get_action_time():
    action_times = [0xfd2c030, 0x18c120b0, 0xdd98840, 0x13ee8a0, 0x1a26560, 0x21526d10, 0xe100190, 0xfbf3830]  # Todo how are those generated
    current_time = (datetime.datetime.utcnow() - datetime.datetime(1,1,1)).total_seconds() * 10**7
    time_offset = random.choice(action_times)
    print(time_offset)
    next_time = int(current_time + time_offset)
    final_time = (next_time & 0x3FFFFFFFFFFFFFFF) - 0x701CE1722770000
    return final_time, next_time


def check_action_time(action_time):
    return action_time < (datetime.datetime.utcnow() - datetime.datetime(1,1,1)).total_seconds() * 10**7


class BaseApi:
    URL = "https://api-sinoalice-us.pokelabo.jp"
    BN_PAYMENT_URL = "https://bn-payment-us.wrightflyer.net"
    BN_MODERATION_URL = "https://bn-moderation-us.wrightflyer.net"

    crypto_key = b"***REMOVED***"  # Reverse: Static, Unity part, BasicCrypto.encrypt
    app_secret_payment = "***REMOVED***"   # Reverse: Static, Java Part, .sign.AuthorizedSigner constructor
    app_secret_moderation = "***REMOVED***"  # Reverse: Static, Java Part, .sign.DefaultSigner constructor
    app_id = "***REMOVED***"  # Reverse: Static, web log

    def __init__(self, player_information: PlayerInformation = None):
        self.request_session = requests.session()
        self.request_session.verify = False

        self.player_information = player_information
        if player_information is None:
            self.player_information = PlayerInformation()

        self.device_info = DeviceInfo()
        self.session_id: str = ""
        self.action_time, self.action_time_ticks = get_action_time()

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
            "payload": json.dumps(device_info_dict).replace(" ", "")
        }

        login_payload_bytes = json.dumps(login_payload).encode()
        authorization = self._build_oauth_header_entry("POST", self.BN_PAYMENT_URL + auth_initialize,
                                                       login_payload_bytes, self.app_secret_payment, new_account=True)

        header = self.device_info.get_bn_payment_header(authorization)
        header["Authorization"] = authorization
        self.request_session.headers = header

        response = self.request_session.post(self.BN_PAYMENT_URL + auth_initialize, login_payload_bytes)
        self.player_information.uuid_payment = response.json()["uuid"]

        auth_x_uid = "/v1.0/auth/x_uid"
        authorization = self._build_oauth_header_entry("GET", self.BN_PAYMENT_URL + auth_x_uid, b"",
                                                       self.app_secret_payment, self.player_information.private_key_payment)

        header["Authorization"] = authorization
        response = self.request_session.get(self.BN_PAYMENT_URL + auth_x_uid)
        self.player_information.x_uid_payment = response.json()["x_uid"]

    def _moderation_registration(self):
        auth_initialize = "/v1.0/auth/initialize"

        device_info_dict = self.device_info.get_device_info_dict()
        device_info_dict["uuid"] = self.player_information.uuid_payment
        device_info_dict["xuid"] = 0

        login_payload = {
            "device_id": f"{self.player_information.device_id}",
            "token": f"{self.player_information.private_key_moderation.publickey().export_key().decode()}",
            "payload": json.dumps(device_info_dict).replace(" ", "")
        }

        login_payload_bytes = json.dumps(login_payload)
        authorization = self._build_oauth_header_entry("POST", self.BN_MODERATION_URL + auth_initialize,
                                                       login_payload_bytes.encode(), self.app_secret_moderation, new_account=True)

        header = self.device_info.get_bn_moderation_header(authorization)

        self.request_session.headers = header
        response = self.request_session.post(self.BN_MODERATION_URL + auth_initialize, login_payload_bytes)
        self.player_information.uuid_moderation = response.json()["uuid"]

    def _login_account(self):
        inner_payload = self.device_info.get_device_info_dict()
        inner_payload["uuid"] = self.player_information.uuid_payment
        inner_payload["xuid"] = int(self.player_information.x_uid_payment)

        response = self._post("/api/login", inner_payload, remove_header={'Cookie'})
        self.session_id = response["payload"]["sessionId"]
        self.player_information.user_id = response["payload"]["userId"]

    def login(self, new_registration=False):
        if new_registration:
            self._payment_registration()
            self._moderation_registration()
            self._login_account()

        else:
            self._payment_authorize()
        self._payment_device_verification()

    def get_migrate_information(self, password: str):
        migration_endpoint = "/v1.0/migration/code?renew=0"
        authorization = self._build_oauth_header_entry("GET", self.BN_PAYMENT_URL + migration_endpoint,
                                                       b"", self.app_secret_moderation, self.player_information.private_key_payment)

        header = self.device_info.get_bn_payment_header(authorization)
        self.request_session.headers = header
        response = self.request_session.post(self.BN_MODERATION_URL + migration_endpoint)
        print(response.content)

        migration_password_endpoint = "/v1.0/migration/password/register"
        payload = {"migration_password": "=RGLuSJLuSJL"}
        payload = json.dumps(payload).encode()

        authorization = self._build_oauth_header_entry("POST", self.BN_PAYMENT_URL + migration_password_endpoint,
                                                       payload, self.app_secret_moderation, self.player_information.private_key_payment)

        header = self.device_info.get_bn_payment_header(authorization)
        self.request_session.headers = header
        response = self.request_session.post(self.BN_MODERATION_URL + migration_password_endpoint, payload)
        print(response.content)


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
            oauth_header["xoauth_requestor_id"] = self.player_information.uuid_payment

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

    def _generate_signature(self, data: bytes, hash_function, key, base=False):
        hashed_string = hash_function.new(data)
        if base:
            base_string = base64.b64encode(hashed_string.digest())
            hashed_string = hash_function.new()
            hashed_string.update(base_string)
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


    def _prepare_request(self, request_type, resource, inner_payload: dict, remove_header=None):
        if remove_header is None:
            remove_header = []

        if not check_action_time(self.action_time_ticks):
            self.action_time, self.action_time_ticks = get_action_time()
            logging.debug(f"Setting new action time {self.action_time}")
        if "exec" in resource:
            self.action_time, self.action_time_ticks = get_action_time()


        payload = {
            "payload": inner_payload,
            "uuid": self.player_information.uuid_payment,
            "userId": self.player_information.user_id,
            "sessionId": self.session_id,
            "actionToken": None,
            "ctag": None,
            "actionTime": self.action_time
        }

        logging.info(f"Payload of {self.player_information.uuid_payment} {payload}")

        payload = self._encrypt_request(payload)

        mac = self._generate_signature(payload, SHA1, self.player_information.private_key_payment, base=True).strip().decode()

        common_headers = {
            "Expect": "100-continue",
            "User-Agent": f"UnityRequest com.nexon.sinoalice {self.device_info.appVersion} ({self.device_info.deviceModel}"
                          f" Android OS 10 / API-29)",
            "X-post-signature": f"{mac}",
            "X-Unity-Version": "2018.4.19f1",
            "Content-Type": "application/x-msgpack",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": f"{self.session_id}",
            "Host": "api-sinoalice-us.pokelabo.jp",

        }
        for header in remove_header:
            common_headers.pop(header)

        self.request_session.headers = common_headers
        return payload

    def _handle_response(self, response):
        decrypted_response = self._decrypt_response(response.content)
        logging.info(f"response of {self.player_information.uuid_payment} {decrypted_response}")
        code = response.status_code
        return decrypted_response

    def _get(self, resource, params=None):
        if params is None:
            params = {}
        url = BaseApi.URL + resource

        self._prepare_request("GET", resource, {})
        response = self.request_session.get(url, params=params)
        return self._handle_response(response)

    def _post(self, resource, payload: dict = None, remove_header=None):
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

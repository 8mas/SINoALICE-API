from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA1

from api.Constants.ErrorCodes import *
from api.Constants.Secrets import CRYPTO_KEY, APP_VERSION
from api.OAuth.OAuthPayment import OAuthPayment
from api.OAuth.OAuthModeration import OAuthModeration

import requests
import logging
import msgpack
import base64
import time
import datetime
import random

from .DeviceInformation import DeviceInfo
from .PlayerInformation import PlayerInformation

requests.packages.urllib3.disable_warnings()
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

DEBUG = True

def get_action_time(old_action_time=0):
    action_times = [0xfd2c030, 0x18c120b0, 0xdd98840, 0x13ee8a0, 0x1a26560, 0x21526d10, 0xe100190, 0xfbf3830]  # Todo how are those generated
    current_time = (datetime.datetime.utcnow() - datetime.datetime(1,1,1)).total_seconds() * 10**7
    time_offset = random.choice(action_times)
    next_time = int(current_time + time_offset)
    final_time = ((next_time & 0x3FFFFFFFFFFFFFFF) - 0x701CE1722770000)
    return final_time


def check_action_time(action_time):
    return action_time < (datetime.datetime.utcnow() - datetime.datetime(1,1,1)).total_seconds() * 10**7

class BaseApi:
    URL = "https://api-sinoalice-us.pokelabo.jp"

    def __init__(self, player_information: PlayerInformation = None):
        self.request_session = requests.session()
        self.request_session.verify = False

        self.device_info = DeviceInfo()
        self.player_information = player_information
        if player_information is None:
            self.player_information = PlayerInformation()

        self.oauth_payment = OAuthPayment(self.device_info, self.player_information.private_key_payment,
                                          self.player_information.device_id, self.request_session)
        self.oauth_moderation = OAuthModeration(self.device_info, self.player_information.private_key_moderation,
                                                self.player_information.device_id, self.request_session)  # Payment is right

        self.session_id: str = ""
        self.action_time = get_action_time()

        # Use local proxy
        if DEBUG:
            logging.info("Using proxy")
            self.request_session.proxies.update({"http": "http://127.0.0.1:8888", "https": "https://127.0.0.1:8888", })

    def _login_account(self):
        inner_payload = self.device_info.get_device_info_dict()
        inner_payload["uuid"] = self.player_information.uuid_payment
        inner_payload["xuid"] = int(self.player_information.x_uid_payment)

        response = self._post("/api/login", inner_payload, remove_header={'Cookie'})
        self.session_id = response["payload"]["sessionId"]
        self.player_information.user_id = response["payload"]["userId"]

    def login(self, new_registration=False):
        if new_registration:
            self.oauth_payment.payment_registration()
            self.player_information.uuid_payment = self.oauth_payment.uuid
            self.player_information.x_uid_payment = self.oauth_payment.x_uid

            self.oauth_moderation.moderation_registration(self.player_information.uuid_payment)
            self.player_information.uuid_moderation = self.oauth_moderation.uuid
        else:
            self.oauth_payment.payment_authorize()

        self._login_account()
        self.oauth_payment.payment_device_verification()

    def get_migrate_information(self, password):
        self.oauth_payment.get_migrate_information(password)
        self.player_information.transfer_code = self.oauth_payment.migration_code
        self.player_information.transfer_password = password

    def _generate_signature(self, data: bytes, hash_function, key):
        hashed_string = hash_function.new(data)
        base_string = base64.b64encode(hashed_string.digest())
        hashed_string = hash_function.new()
        hashed_string.update(base_string)
        signature = pkcs1_15.new(key).sign(hashed_string)
        return base64.b64encode(signature)

    def _decrypt_response(self, response_content: bytes) -> dict:
        iv = response_content[0:16]
        aes = AES.new(CRYPTO_KEY, AES.MODE_CBC, iv)
        pad_text = aes.decrypt(response_content[16:])
        text = unpad(pad_text, 16)
        data_loaded = msgpack.unpackb(text)
        return data_loaded

    def _encrypt_request(self, request_content: dict):
        packed_request_content = msgpack.packb(request_content)
        iv = packed_request_content[0:16]
        padded_request_content = pad(packed_request_content, 16)
        aes = AES.new(CRYPTO_KEY, AES.MODE_CBC, iv)
        encrypted_request_content = aes.encrypt(padded_request_content)
        return iv + encrypted_request_content

    def _prepare_request(self, request_type, resource, inner_payload: dict, remove_header=None):
        self.last_request = request_type, resource, inner_payload, remove_header, time.time()

        if remove_header is None:
            remove_header = []

        self.action_time = get_action_time()

        payload = {
            "payload": inner_payload,
            "uuid": self.player_information.uuid_payment,
            "userId": self.player_information.user_id,
            "sessionId": self.session_id,
            "actionToken": None,
            "ctag": None,
            "actionTime": self.action_time
        }

        logging.debug(f"to {resource} {payload} {self.player_information.uuid_payment}")

        payload = self._encrypt_request(payload)

        mac = self._generate_signature(payload, SHA1, self.player_information.private_key_payment).strip().decode()

        common_headers = {
            "Expect": "100-continue",
            "User-Agent": f"UnityRequest com.nexon.sinoalice {APP_VERSION} ({self.device_info.deviceModel}"
                          f" Android OS 10 / API-29)",
            "X-post-signature": f"{mac}",
            "X-Unity-Version": "2018.4.19f1",
            "Content-Type": "application/x-msgpack",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": f"{self.session_id}",
            "Host": "api-sinoalice-us.pokelabo.jp"
        }
        for header in remove_header:
            common_headers.pop(header)

        self.request_session.headers = common_headers
        return payload

    def _handle_response(self, response):
        decrypted_response = self._decrypt_response(response.content)
        logging.debug(f"from {response.request.path_url} {decrypted_response}")
        code = response.status_code

        if decrypted_response.get("errors", None) is not None:
            if decrypted_response["errors"][0]["code"] == EXCESS_TRAFFIC:
                logging.warning(f"EXCESS_TRAFFIC Exception {response.request.path_url}")
                raise ExcessTrafficException("")

        return decrypted_response

    def _get(self, resource, params=None):
        if params is None:
            params = {}
        url = BaseApi.URL + resource

        self._prepare_request("GET", resource, {})
        response = self.request_session.get(url, params=params)
        return self._handle_response(response)

    def _post(self, resource, payload: dict = None, remove_header=None) -> dict:
        url = BaseApi.URL + resource

        payload = self._prepare_request("POST", resource, payload, remove_header=remove_header)

        resulting_response = None
        timeout_duration = 10
        while resulting_response is None:
            response = self.request_session.post(url, payload)
            try:
                resulting_response = self._handle_response(response)
            except ExcessTrafficException as e:
                time.sleep(timeout_duration)
                timeout_duration += 5
                if timeout_duration > 300:
                    logging.critical(f"Maximum attempts for {resource} aborting")
                    exit(-1)
        return resulting_response

    def _put(self):
        pass

    def _delete(self):
        pass


class SigningException(Exception):
    pass

class ExcessTrafficException(Exception):
    pass
from api.OAuth.OAuthCrypto import OAuthCrypto
from api.Constants.Secrets import APP_VERSION, APP_SECRET_PAYMENT
import json
import codecs
import base64
import logging


class OAuthPayment:
    BN_PAYMENT_URL = "https://bn-payment-us.wrightflyer.net"

    def __init__(self, device_info, rsa_key, device_id, request_session):
        self.device_info = device_info
        self.rsa_key = rsa_key
        self.device_id = device_id
        self.request_session = request_session
        self.uuid = None
        self.x_uid = None
        self.oauth_crypto = OAuthCrypto(APP_SECRET_PAYMENT, self.rsa_key)

    def _prepare_request(self, rest_type: str, resource: str, data, extra_header=None):
        new_account = self.uuid is None
        authorization = self.oauth_crypto.build_oauth_header_entry(rest_type, self.BN_PAYMENT_URL + resource,
                                                                   data, self.uuid, new_account,
                                                                   extra_header)

        header = self.device_info.get_bn_payment_header(authorization)
        self.request_session.headers = header

    def get_migrate_information(self, password: str):
        migration_endpoint = "/v1.0/migration/code"
        extra_header = {"renew": "0"}

        self._prepare_request("GET", migration_endpoint, b"", extra_header)
        response = self.request_session.get(self.BN_PAYMENT_URL + migration_endpoint + "?renew=0")

        logging.info(f"Migration code: {response.content.decode()}")

        password = codecs.encode(base64.b64encode(password.encode())[::-1].decode(), "rot_13")

        migration_password_endpoint = "/v1.0/migration/password/register"
        payload = {"migration_password": password}
        payload = json.dumps(payload).encode()

        self._prepare_request("POST", migration_password_endpoint, payload)
        response = self.request_session.post(self.BN_PAYMENT_URL + migration_password_endpoint, payload)
        logging.debug(f"Migration code password set: {response.content.decode()}")


    # We can not fake a attestation :/ we can leave it empty or throw an error that is defined in the app
    def payment_device_verification(self):
        nonce = "/v1.0/deviceverification/nonce"

        self._prepare_request("POST", nonce, b"")
        self.request_session.post(self.BN_PAYMENT_URL + nonce)

        verify_endpoint = "/v1.0/deviceverification/verify"
        verification_payload = {
            "device_id": f"{self.device_id}",
            "compromised": False,
            "emulator": False,
            "debug": False,
            "installer": "com.android.vending",
            "bundle_id": "com.nexon.sinoalice",
            "app_version": APP_VERSION,
            "os_version": "10",
            "sf_jws": ""
        }

        payload = json.dumps(verification_payload).encode()

        self._prepare_request("POST", verify_endpoint, payload)
        self.request_session.post(self.BN_PAYMENT_URL + verify_endpoint, payload)

    def payment_authorize(self):
        authorize_endpoint = "/v1.0/auth/authorize"

        self._prepare_request("POST", authorize_endpoint, b"")
        self.request_session.post(self.BN_PAYMENT_URL + authorize_endpoint)

    def payment_registration(self):
        auth_initialize = "/v1.0/auth/initialize"
        auth_x_uid = "/v1.0/auth/x_uid"

        device_info_dict = self.device_info.get_device_info_dict()
        device_info_dict["uuid"] = None
        device_info_dict["xuid"] = 0

        login_payload = {
            "device_id": f"{self.device_id}",
            "token": f"{self.rsa_key.publickey().export_key().decode()}",
            "payload": json.dumps(device_info_dict).replace(" ", "")
        }

        login_payload_bytes = json.dumps(login_payload).encode()

        self._prepare_request("POST", auth_initialize, login_payload_bytes)
        response = self.request_session.post(self.BN_PAYMENT_URL + auth_initialize, login_payload_bytes)
        self.uuid = response.json()["uuid"]

        self._prepare_request("GET", auth_x_uid, b"")
        response = self.request_session.get(self.BN_PAYMENT_URL + auth_x_uid)
        self.x_uid = response.json()["x_uid"]

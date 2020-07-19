from api.Constants.Secrets import APP_SECRET_MODERATION
from api.OAuth.OAuthCrypto import OAuthCrypto
import json


class OAuthModeration:
    BN_MODERATION_URL = "https://bn-moderation-us.wrightflyer.net"

    def __init__(self, device_info, rsa_key, device_id, request_session):
        self.device_info = device_info
        self.rsa_key = rsa_key
        self.device_id = device_id
        self.request_session = request_session
        self.uuid = None
        self.x_uid = None
        self.oauth_crypto = OAuthCrypto(APP_SECRET_MODERATION, self.rsa_key)

    def moderation_registration(self, uuid_payment):
        auth_initialize = "/v1.0/auth/initialize"

        device_info_dict = self.device_info.get_device_info_dict()
        device_info_dict["uuid"] = uuid_payment
        device_info_dict["xuid"] = 0

        login_payload = {
            "device_id": f"{self.device_id}",
            "token": f"{self.rsa_key.publickey().export_key().decode()}",
            "payload": json.dumps(device_info_dict).replace(" ", "")
        }

        login_payload = json.dumps(login_payload)
        login_payload_bytes = login_payload.encode()
        authorization = self.oauth_crypto.build_oauth_header_entry("POST", self.BN_MODERATION_URL + auth_initialize,
                                                                   login_payload_bytes, new_account=True)

        header = self.device_info.get_bn_moderation_header(authorization)

        self.request_session.headers = header
        response = self.request_session.post(self.BN_MODERATION_URL + auth_initialize, login_payload)
        self.uuid = response.json()["uuid"]

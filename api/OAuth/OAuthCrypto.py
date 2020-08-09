from typing import Optional, Dict, Any

from Crypto.Hash import SHA1
from urllib.parse import quote_plus
from Crypto.Signature import pkcs1_15
from api.Constants.Secrets import APP_ID

import hmac
import base64
import time
import random


def generate_signature(data: bytes, hash_function, key):
    hashed_string = hash_function.new(data)
    signature = pkcs1_15.new(key).sign(hashed_string)
    return base64.b64encode(signature)


def generate_nonce(length=19):
    return int(''.join([str(random.randint(0, 9)) for i in range(length)]))


class OAuthCrypto:

    def __init__(self, app_secret, rsa_key):
        self.app_secret = app_secret
        self.rsa_key = rsa_key

    def build_oauth_header_entry(self, rest_method: str, full_url: str, body_data: bytes, uuid: Optional[str] = None,
                                 new_account: bool=False, extra_header: Dict[str, Any]=None):

        timestamp = int(time.time())
        oauth_header = {
            "oauth_body_hash": f"{base64.b64encode(SHA1.new(body_data).digest()).decode()}",
            "oauth_consumer_key": f"{APP_ID}",
            "oauth_nonce": f"{generate_nonce()}",
            "oauth_signature_method": f"{'HMAC-SHA1' if new_account else 'RSA-SHA1'}",
            "oauth_timestamp": f"{timestamp}",
            "oauth_version": "1.0"
        }

        oauth_header.update(extra_header or {})

        if not new_account:
            to_hash = (self.app_secret + str(timestamp)).encode()
            param_signature = generate_signature(to_hash, SHA1, self.rsa_key)
            oauth_header["xoauth_as_hash"] = param_signature.strip()
            oauth_header["xoauth_requestor_id"] = uuid

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
                         quote_plus(auth_string.rsplit("&", 1)[0])  # Todo: Comment

        if new_account:
            oauth_signature = hmac.new(self.app_secret.encode(), string_to_hash.encode(), "SHA1").digest()
            oauth_signature = base64.b64encode(oauth_signature)
        else:
            oauth_signature = generate_signature(string_to_hash.encode(), SHA1, self.rsa_key)

        oauth_header["oauth_signature"] = oauth_signature

        oauth_header_entry = "OAuth "
        for key, value in sorted(oauth_header.items()):
            oauth_header_entry += key
            oauth_header_entry += "=\""
            oauth_header_entry += quote_plus(value)
            oauth_header_entry += "\","
        oauth_header_entry = oauth_header_entry[:-1]
        return oauth_header_entry

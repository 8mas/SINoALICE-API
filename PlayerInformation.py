from dataclasses import dataclass
from Crypto.PublicKey.RSA import RsaKey


@dataclass(unsafe_hash=True)
class PlayerInformation:
    server: str
    device_id: str
    uuid_payment: str
    uuid_moderation: str
    x_uid_payment: str
    x_uid_moderation: str
    private_key_payment: RsaKey
    private_key_moderation: RsaKey
    user_id: int

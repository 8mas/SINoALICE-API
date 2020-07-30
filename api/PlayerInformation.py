from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Interval, String, Integer, Boolean
from sqlalchemy import orm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from Crypto.PublicKey.RSA import RsaKey
from Crypto.PublicKey import RSA
import random
import codecs
import base64

Base = declarative_base()

def generate_device_id():
    id = "".join([random.choice("abcdef1234567890") for _ in range(16)])
    encoded_id = codecs.encode(base64.b64encode(id.encode())[::-1].decode(), "rot_13")
    return encoded_id


class PlayerInformation(Base):
    __tablename__ = "PlayerInformation"

    server: str = Column(String)
    transfer_code: str = Column(String)
    transfer_password: str = Column(String)
    ss_rare: int = Column(Integer)
    item_names: str = Column(String)
    nightmare_names: str = Column(String)
    character_names: int = Column(Integer)

    item_ids: str = Column(String)
    character_ids: str = Column(String)
    sold: bool = Column(Boolean)


    uuid_payment: str = Column(String, primary_key=True)  # static, This is in the first response when sending app id
    uuid_moderation: str = Column(String)  # static, This is in the first response when sending app id
    x_uid_payment: str = Column(String)  # static, response to auth/x_uid, this is also the playerID
    x_uid_moderation: str = Column(String)  # static, response to auth/x_uid TODO Not used yet + what is this for

    device_id: str = Column(String)  # android id
    _private_key_payment: str = Column(String)
    _private_key_moderation: str = Column(String)
    user_id: int = Column(Integer)  # static, response to api login



    private_key_payment: RsaKey = RSA.generate(512)
    private_key_moderation: RsaKey = RSA.generate(512)

    def __init__(self):
        if self.server is None:
            self.server = "US"

        self.device_id = generate_device_id()
        self._private_key_payment = self.private_key_payment.export_key().decode()
        self._private_key_moderation = self.private_key_moderation.export_key().decode()

    @orm.reconstructor
    def after_construction_by_alchemy(self):
        self.private_key_payment = RSA.import_key(self._private_key_payment)
        self.private_key_moderation = RSA.import_key(self._private_key_moderation)

    @staticmethod
    def create_db(db_name):
        engine = create_engine(f"sqlite:///{db_name}")
        Base.metadata.create_all(engine)

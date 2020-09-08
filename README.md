# SinoAliceApi
This project provides the foundation for using the [SINoAlice API](/api).

Furthermore a [farming Bot](/bot) for SINoAlice is implemented (Work in Progress)

The secret API keys for encryption, oauth and MACs are __not__ included here and have to be reverse engineered by oneself.
(these must be specified in the Secrets.py)

To enable RSA with 512 bit you may have to change RSA.py. (PyCryptodome Crypto.PublicKey.RSA) You can probably also use 1024 bit keys, but this will differ from the SINoALICE API.
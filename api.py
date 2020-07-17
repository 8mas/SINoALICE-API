from api_base import BaseApi
import json

DEBUG = True


class API(BaseApi):
    def __init__(self):
        BaseApi.__init__(self)

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
                "uuid": None,  # TODO check
                "xuid": 928750150,  # TODO check
                "locale": "en_US",
                "numericCountryCode": 826  # TODO check
            },
            "uuid": "***REMOVED***636a36e2c5f747fdb12e059a5f830369",  # Todo generate
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

    a.login(True)

from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class DeviceInfo:
    appVersion: str = "1.5.0"
    deviceModel: str = "Samsung Galaxy Note10"
    numericCountryCode: int = 840

    carrier: str = "Vodafone"
    country_code: str = "US"
    auth_version: str = "1.4.10"
    store_type: str = "google"
    uaType: str = "android-app"
    currency_code: str = "USD"

    us_or_jp = "us"
    host_payment: str = f"bn-payment-{us_or_jp}.wrightflyer.net"
    host_moderation: str = f"bn-moderation-{us_or_jp}.wrightflyer.net"

    bn_payment_header = {
        "Authorization": None,
        "X-GREE-GAMELIB": f"authVersion%3D{auth_version}%26storeType%3D{store_type}%26appVersion%3D{appVersion}"
                          f"%26uaType%3D{uaType}%26carrier%3D{carrier}%26compromised%3Dfalse"
                          f"%26countryCode%3D{country_code}%26currencyCode%3D{currency_code}",

        "User-Agent": f"Mozilla/5.0 (Linux; Android 10; {deviceModel} AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.101 Mobile Safari/537.36",
        "Content-Type": "application/json; charset=UTF-8",
        "Host": host_payment,
        "Accept-Encoding": "gzip",
        "Connection": "keep-alive"
    }

    bn_moderation_header = {
        "Authorization": None,
        "X-GREE-GAMELIB": f"authVersion%3D{auth_version}%26appVersion%3D{appVersion}%26uaType%3D{uaType}"
                          f"%26carrier%3D{carrier}%26compromised%3Dfalse%26countryCode%3D{country_code}"
                          f"%26currencyCode%3D{currency_code}",

        "User-Agent": f"Mozilla/5.0 (Linux; Android 10; {deviceModel} AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.101 Mobile Safari/537.36",
        "Content-Type": "application/json; charset=UTF-8",
        "Host": host_moderation,
        "Accept-Encoding": "gzip",
        "Connection": "keep-alive"
    }

    device_info_dict = {
        "appVersion": appVersion,
        "urlParam": None,
        "deviceModel": deviceModel,
        "osType": 2,
        "osVersion": "Android OS 10 / API-29",
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
        "uuid": None,
        "xuid": 0,
        "locale": "en_US",
        "numericCountryCode": numericCountryCode
    }
from api_base import BaseApi
import json

DEBUG = True


class API(BaseApi):
    def __init__(self):
        BaseApi.__init__(self)

    def POST__api_user_get_user_data(self):
        self._post("/api/user/get_user_data", None)

    def POST__api_config_get_config(self):
        self._post("/api/config/get_config", None)

    def POST__api_tutorial_get_next_tutorial_mst_id(self):
        self._post("/api/tutorial/get_next_tutorial_mst_id", None)

    def POST__api_tutorial_agree_legal_document(self):
        self._post("/api/tutorial/agree_legal_document", None)

    def POST__api_tutorial_get_tutorial_gacha(self):
        self._post("/api/tutorial/get_tutorial_gacha", None)

    def POST__api_tutorial_fxm_tutorial_gacha_drawn_result(self):
        # TODO check results
        self._post("/api/tutorial/fxm_tutorial_gacha_drawn_result", None)

    def POST__api_tutorial_fxm_tutorial_gacha_exec(self):
        self._post("/api/tutorial/fxm_tutorial_gacha_exec", None)

    def POST__api_tutorial_get_user_mini_tutorial_data(self):
        self._post("/api/tutorial/get_user_mini_tutorial_data", None)

class SigningException(Exception):
    pass

from api.BaseApi import BaseApi


class API(BaseApi):
    def __init__(self):
        BaseApi.__init__(self)

    def POST__api_user_get_user_data(self):
        self._post("/api/user/get_user_data")

    def POST__api_config_get_config(self):
        self._post("/api/config/get_config")

    def POST__api_tutorial_get_next_tutorial_mst_id(self):
        self._post("/api/tutorial/get_next_tutorial_mst_id")

    def POST__api_tutorial_agree_legal_document(self):
        self._post("/api/tutorial/agree_legal_document")

    def POST__api_tutorial_get_tutorial_gacha(self):
        self._post("/api/tutorial/get_tutorial_gacha")

    def POST__api_tutorial_fxm_tutorial_gacha_drawn_result(self):
        # TODO check results
        self._post("/api/tutorial/fxm_tutorial_gacha_drawn_result")

    def POST__api_tutorial_fxm_tutorial_gacha_exec(self):
        self._post("/api/tutorial/fxm_tutorial_gacha_exec")

    def POST__api_tutorial_get_user_mini_tutorial_data(self):
        self._post("/api/tutorial/get_user_mini_tutorial_data")

    def POST__api_tutorial_set_user_name(self, name: str):
        payload = {
            "userName": name
        }
        self._post("/api/tutorial/set_user_name", payload)

    def POST__api_tutorial_set_character(self, character_id):
        payload = {
            "characterMstId": character_id
        }
        self._post("/api/tutorial/set_character", payload)

    def POST__api_cleaning_check(self):
        payload = {}
        self._post("/api/cleaning/check", payload)

    def POST__api_cleaning_start(self, cleaning_type=1):
        payload = {
            "cleaningType": cleaning_type
        }
        self._post("/api/cleaning/start", payload)

    def POST__api_cleaning_end_wave(self, remain_time, current_wave, ap, exp, enemy_down):
        payload = {
            "remainTime": remain_time,
            "currentWave": current_wave,
            "getAp": ap,
            "getExp": exp,
            "getEnemyDown": enemy_down
        }
        self._post("/api/cleaning/end_wave", payload)

    def POST__api_cleaning_end(self, end_wave):
        payload = {
            "remainTime": 0,
            "currentWave": end_wave,
            "getAp": 0,
            "getExp": 0,
            "getEnemyDown": 0
        }
        self._post("/api/cleaning/end", payload)

    def POST__api_cleaning_retire(self):
        self._post("/api/cleaning/retire")

class SigningException(Exception):
    pass

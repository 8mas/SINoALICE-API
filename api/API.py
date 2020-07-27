from api.BaseApi import BaseApi
from api.ParseResourceData import character_dict, card_dict
import logging

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

    def POST__api_tutorial_fxm_tutorial_gacha_drawn_result(self) -> (int, int, int):
        response = self._post("/api/tutorial/fxm_tutorial_gacha_drawn_result")

        item_names = []
        num_ssrare = 0
        num_srare = 0
        num_characters = 0

        for result in response["payload"]["result"]:
            rarity = int(result["rarity"])
            object_id = str(result["objectId"])
            character_id = str(result["characterMstId"])

            if character_id != "0":
                to_append = str(rarity) + ":" + str(character_dict[character_id]["name"])
                item_names.append(to_append)
            else:
                to_append = str(rarity) + ":" + card_dict[object_id]["name"]
                item_names.append(to_append)

            if rarity > 5:
                logging.info("Got rarity >5")
            if rarity == 5:
                num_ssrare += 1
            if rarity == 4:
                num_srare += 1
            if character_id != "0":
                num_characters += 1

        self.player_information.ss_rare = num_ssrare
        self.player_information.s_rare = num_srare
        self.player_information.characters = num_characters
        self.player_information.item_names = str(item_names)

        logging.info(f"Gacha result SS:{num_ssrare} S:{num_srare} Chars:{num_characters} Names: {item_names}")

        return num_ssrare, num_srare, num_characters, item_names

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


    def POST__api_quest_get_attention(self):
        self._post("/api/quest/get_attention")

    def POST__api_quest_get_alice_area_map(self):
        payload = {
            "questMapMstId": 1,
        }
        self._post("/api/quest/get_alice_area_map", payload)

    def POST__api_quest_get_alice_stage_list(self):
        payload = {
            "questAreaMstId": 6,
            "battleNum": 0
        }
        self._post("/api/quest/get_alice_stage_list", payload)

    def POST__api_quest_get_stage_data(self):
        payload = {
            "questStageMstId": 51
        }
        self._post("/api/quest/get_stage_data", payload)

    def POST__api_quest_get_stage_reward(self):
        payload = {
            "questStageMstId": 51
        }
        self._post("/api/quest/get_stage_reward", payload)

    def POST__api_quest_get_tutorial_result(self):
        payload =  {"questStageMstId": 51, "characterMstId": 2}
        self._post("/api/quest/get_tutorial_result", payload)

    def POST__api_tutorial_finish_mini_tutorial(self):
        payload = {
            "miniTutorialMstId": 34
        }
        self._post("/api/tutorial/finish_mini_tutorial", payload)

    def POST__api_present_get_present_data(self):
        response = self._post("/api/present/get_present_data")
        presents = response["payload"]["presentData"]

        present_id_list = []
        for json_present in presents:
            present_id_list.append(json_present["presentDataId"])

        return present_id_list

    def POST__api_present_gain_present(self, present_id_list):
        payload = {
            "sendCardStorageFlag": False,
            "presentDataId": present_id_list
        }

        self._post("/api/present/gain_present", payload)

    #mstID = which banner 23 = nier
    def POST__api_gacha_gacha_exec(self):
        payload = {
            "gachaMstId": 23,
            "gachaType": 1
        }
        self._post("/api/gacha/gacha_exec", payload)



    def POST__api_character_get_character_data_list(self):
        response = self._post("/api/character/get_character_data_list")
        data = response["payload"]["characterDataList"]

        char_names = []
        all_ids = []

        for char in data:
            id = str(char["characterMstId"])
            all_ids.append(int(id))
            item_name = character_dict[id]["name"]
            name = item_name
            char_names.append(name)

        return char_names, all_ids

    def POST__api_card_info_get_card_data_by_user_id(self):
        response = self._post("/api/card_info/get_card_data_by_user_id" )
        data = response["payload"]["cardDataList"]

        item_names = []
        nightmares = []
        all_ids = []

        for card in data:
            id = str(card["cardMstId"])
            all_ids.append(int(id))

            item_name = card_dict[id]["name"]
            item_rarity = card_dict[id]["rarity"]

            name = str(item_rarity) + ":" + item_name

            if card_dict[id]["cardType"] == 3:
                nightmares.append(name)
            else:
                item_names.append(name)

        return item_names, nightmares, all_ids


class SigningException(Exception):
    pass

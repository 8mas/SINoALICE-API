import logging
import sys
import time
import random
from api.API import API
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.PlayerInformation import PlayerInformation
from api.ParseResourceData import character_dict, card_dict

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("sinoalice.log", "w", "utf-8")
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)


common_names = ["Ninja", "Ryu", "Nathan", "Ashley", "Kasumi", "Leon", "Adam", "Shepard",
                "James", "John", "David", "Richard", "Maria", "Donald"]

"""
SETTINGS
2SR + Cinderella + A2 Sword + other SR swords + Nightmare 

"""
# Items
TYPE_40_BLADE = 811
BEASTLORD = 927
CRUEL_ARROGANCE = 813
VIRTUOUS_CONTRACT = 815
NO_7_STAFF = 817

# Nightmares
UGALLU = 457
FREEZE_GOLEM = 479
LINDWYRM = 516

# Chars
GRETEL_MINSTREL = 19
CINDERELLA_BREAKER = 21
ALICE_CLERIC = 22


TUTORIAL_SS_MIN = 1  # Number of min SS rares
TUTORIAL_OVERRIDE_SS_MIN = 4  # If so much SS rares are in the gacha, take it
TUTORIAL_CHAR_MUST_HAVE_IDS = {GRETEL_MINSTREL, CINDERELLA_BREAKER,
                               ALICE_CLERIC}  # This is an OR e.g. 24 or 7 must be there

GACHA_TYPE = 23  # Neir Gacha
GACHA_MUST_HAVE_ITEM_IDS = {TYPE_40_BLADE, BEASTLORD, CRUEL_ARROGANCE, VIRTUOUS_CONTRACT, NO_7_STAFF}  # Item ids for normal items
GACHA_MUST_HAVE_NIGHTMARE_IDS = {UGALLU, FREEZE_GOLEM, LINDWYRM}


class Bot:
    def __init__(self):
        self.api = API()

    def create_new_account(self):
        self.api.login(new_registration=True)

        self.api.POST__api_user_get_user_data()
        self.api.POST__api_config_get_config()
        self.api.POST__api_tutorial_get_next_tutorial_mst_id()
        self.api.POST__api_tutorial_agree_legal_document()
        self.api.POST__api_tutorial_get_user_mini_tutorial_data()
        self.api.POST__api_tutorial_get_tutorial_gacha()

        # Loop
        num_ssrare = 0
        while num_ssrare < TUTORIAL_OVERRIDE_SS_MIN:
            time.sleep(11)
            num_ssrare, item_ids, character_ids = self.api.POST__api_tutorial_fxm_tutorial_gacha_drawn_result()
            logging.info("Rolled")
            if set(character_ids) & TUTORIAL_CHAR_MUST_HAVE_IDS and num_ssrare >= TUTORIAL_SS_MIN:
                logging.info(f"New Account {character_ids}")
                break

        self.api.POST__api_tutorial_fxm_tutorial_gacha_exec()
        # Loop End

        name = random.choice(common_names)
        self.api.POST__api_tutorial_set_user_name(name)
        self.api.POST__api_tutorial_set_character(2)
        # Missions
        self.api.POST__api_cleaning_check()
        self.api.POST__api_cleaning_start()
        self.api.POST__api_cleaning_end_wave(25, 1, 5, 5, 5)
        self.api.POST__api_cleaning_end_wave(20, 2, 4, 4, 4)
        self.api.POST__api_cleaning_end_wave(17, 3, 6, 6, 6)
        self.api.POST__api_cleaning_end_wave(14, 4, 6, 6, 6)
        self.api.POST__api_cleaning_end_wave(11, 5, 7, 7, 7)
        self.api.POST__api_cleaning_end_wave(11, 6, 7, 16, 7)
        self.api.POST__api_cleaning_end_wave(6, 7, 0, 16, 7)
        self.api.POST__api_cleaning_end_wave(3, 8, 0, 7, 7)
        self.api.POST__api_cleaning_end_wave(0, 9, 0, 4, 4)
        self.api.POST__api_cleaning_end(10)
        # Missions done
        self.api.POST__api_user_get_user_data()
        self.api.POST__api_tutorial_get_next_tutorial_mst_id()
        self.api.POST__api_cleaning_retire()

    def finish_first_quest(self):
        self.api.POST__api_quest_get_attention()
        self.api.POST__api_quest_get_alice_area_map()
        self.api.POST__api_quest_get_alice_stage_list()
        self.api.POST__api_quest_get_stage_reward()
        self.api.POST__api_quest_get_stage_data()
        self.api.POST__api_quest_get_tutorial_result()

    def get_all_presents(self):
        present_list = self.api.POST__api_present_get_present_data()
        self.api.POST__api_present_gain_present(present_list)

    def play_gacha(self, gacha_id):
        self.api.POST__api_gacha_gacha_exec()
        self.api.POST__api_gacha_gacha_exec()
        self.api.POST__api_gacha_gacha_exec()
        self.api.POST__api_gacha_gacha_exec()
        self.api.POST__api_gacha_gacha_exec()

    def set_player_info_dict(self, character_ids_param, item_ids_param):
        ss_rare = 0
        item_names = ""
        nightmare_names = ""
        character_names = ""

        item_ids = ""
        character_ids = ""

        for char_id in character_ids_param:
            id = str(char_id)
            character_ids += id + ", "
            character_names += character_dict[id]["name"] + ", "

        for item_id in item_ids_param:
            id = str(item_id)
            item_ids += id + ", "
            rarity = str(card_dict[id]["rarity"])
            card_type = card_dict[id]["cardType"]
            to_save = rarity + ":" + card_dict[id]["name"] + ", "

            if rarity == "5":
                ss_rare += 1

            if int(rarity) > 4 or card_type == 3:
                if card_dict[id]["cardType"] == 3:
                    nightmare_names += to_save
                else:
                    item_names += to_save

        self.api.player_information.ss_rare = ss_rare
        self.api.player_information.item_names = item_names
        self.api.player_information.nightmare_names = nightmare_names
        self.api.player_information.character_names = character_names

        self.api.player_information.item_ids = item_ids
        self.api.player_information.character_ids = character_ids

        logging.info(f"Nightmares:{nightmare_names} Items:{item_names} Character:{character_names}")

    def is_good_account(self):
        char_names, chars_ids = self.api.POST__api_character_get_character_data_list()
        item_names, nightmare_names, ids = self.api.POST__api_card_info_get_card_data_by_user_id()

        self.set_player_info_dict(chars_ids, ids)
        if GACHA_MUST_HAVE_NIGHTMARE_IDS & set(ids):
            if GACHA_MUST_HAVE_ITEM_IDS & set(ids):
                logging.info(f"Adding 1x Nightmare and Item account to database {ids} {chars_ids}")
                return True

        if len(GACHA_MUST_HAVE_NIGHTMARE_IDS & set(ids)) > 1:
            logging.info(f"Adding 2x Nightmare account to database {ids} {chars_ids}")
            return True

        if len(TUTORIAL_CHAR_MUST_HAVE_IDS & set(chars_ids)) > 1:
            if GACHA_MUST_HAVE_NIGHTMARE_IDS & set(ids):
                logging.info(f"Adding 2x Class and Nightmare account to database {ids} {chars_ids}")
                return True

        return False

    def migrate(self):
        # Migration
        self.api.get_migrate_information("COSInu11")


def reroll_good_account():
    no_good_account = True
    while no_good_account:
        bot = Bot()
        bot.create_new_account()
        bot.finish_first_quest()
        bot.get_all_presents()
        bot.play_gacha(1)
        if(bot.is_good_account()):
            bot.migrate()
            no_good_account = False
            player_info = bot.api.player_information

    return player_info


if __name__ == "__main__":
    db_name = "sinoalice_accounts.db"
    PlayerInformation.create_db(db_name)
    engine = create_engine(f"sqlite:///{db_name}")
    Session = sessionmaker(bind=engine)
    session = Session()

    future_list = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        for _ in range(1000):
            future = executor.submit(reroll_good_account)
            future_list.append(future)

        for future in as_completed(future_list):
            try:
                player_information = future.result()
                if player_information:
                    session.add(player_information)
                    session.commit()
            except Exception as e:
                logging.warning("An exception occurred, to many threads?")
                print(e)

    logging.info("Finished")
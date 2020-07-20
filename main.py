import logging
import sys
import time
import random
from api.API import API
from concurrent.futures import ThreadPoolExecutor

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("sinoalice.log", "w", "utf-8")
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)


class BotLogic:
    def __init__(self):
        pass


common_names = ["Ninja", "Ryu", "Nathan", "Ashley", "Kasumi", "Leon", "Adam", "Shepard",
                "James", "John", "David", "Richard", "Maria", "Donald"]


def create_new_account():
    a = API()
    a.login(True)
    a.POST__api_user_get_user_data()
    a.POST__api_config_get_config()
    a.POST__api_tutorial_get_next_tutorial_mst_id()
    a.POST__api_tutorial_agree_legal_document()
    a.POST__api_tutorial_get_user_mini_tutorial_data()
    a.POST__api_tutorial_get_tutorial_gacha()
    # Loop
    num_ssrare = 0
    num_characters = 0
    while (num_ssrare < 4 or num_characters < 1) and (num_ssrare < 3 or num_characters < 2) and num_characters < 3\
            and num_ssrare < 5:
        time.sleep(11)
        num_ssrare, num_srare , num_characters, item_names = a.POST__api_tutorial_fxm_tutorial_gacha_drawn_result()

    a.POST__api_tutorial_fxm_tutorial_gacha_exec()
    # Loop End

    name = random.choice(common_names)
    a.POST__api_tutorial_set_user_name(name)
    a.POST__api_tutorial_set_character(2)
    # Missions
    a.POST__api_cleaning_check()
    a.POST__api_cleaning_start()
    a.POST__api_cleaning_end_wave(25, 1, 5, 5, 5)
    a.POST__api_cleaning_end_wave(20, 2, 4, 4, 4)
    a.POST__api_cleaning_end_wave(17, 3, 6, 6, 6)
    a.POST__api_cleaning_end_wave(14, 4, 6, 6, 6)
    a.POST__api_cleaning_end_wave(11, 5, 7, 7, 7)
    a.POST__api_cleaning_end_wave(11, 6, 7, 7, 7)
    a.POST__api_cleaning_end_wave(6, 7, 3, 7, 7)
    a.POST__api_cleaning_end_wave(3, 8, 111110, 111110, 111110)
    a.POST__api_cleaning_end_wave(0, 9, 211110, 321100, 1400)
    a.POST__api_cleaning_end(10)
    # Missions done
    a.POST__api_user_get_user_data()
    a.POST__api_tutorial_get_next_tutorial_mst_id()
    a.POST__api_cleaning_retire()
    # Migration
    a.get_migrate_information("COSInu11")


    """
    2020/07/20 04:01:30 INFO Gacha result SS:4 S:2 Chars:1 Names: ['Holy Lance', "Princess' Pillage", 'Alice/Cleric', 'Sword of Necessary E', 'Ceremonial Spear', "Oracle Knight's Axe", "Retainer's Hammer", 'Savage Crossbow', 'Hammer of Brutality', 'Ruined Gun', 'Naive Miracle Staff']
    b'{"result":"OK","migration_code":"6Q2876N474BDBJ7A"}'
    b'{"result":"OK","migration_code":"WDWG63BNLMJGB56F"}'
    b'{"result":"OK","migration_code":"CMHWNWLS84VL7F7B"}'
    """
if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=10) as executor:
        for _ in range(25):
            executor.submit(create_new_account)
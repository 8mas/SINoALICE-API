import logging
import sys
import time
import random
from api.API import API


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

if __name__ == "__main__":
    a = API()
    a.login(True)
    a.POST__api_user_get_user_data()
    a.POST__api_config_get_config()
    a.POST__api_tutorial_get_next_tutorial_mst_id()
    a.POST__api_tutorial_agree_legal_document()
    a.POST__api_tutorial_get_user_mini_tutorial_data()
    time.sleep(7)
    a.POST__api_tutorial_get_tutorial_gacha()
    # Loop
    time.sleep(7)
    a.POST__api_tutorial_fxm_tutorial_gacha_drawn_result()
    time.sleep(7)
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
    a.POST__api_cleaning_end_wave(3, 8, 0, 6, 6)
    a.POST__api_cleaning_end_wave(0, 9, 100, 100, 100)
    a.POST__api_cleaning_end(10)
    # Missions done
    a.POST__api_user_get_user_data()
    a.POST__api_tutorial_get_next_tutorial_mst_id()
    a.POST__api_cleaning_retire()
    # Migration
    a.get_migrate_information("wtf")
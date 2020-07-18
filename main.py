import logging
import sys
from api import API
import time

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("sinoalice.log")
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)


if __name__ == "__main__":
    a = API()
    a.login(True)
    time.sleep(4)
    a.POST__api_tutorial_agree_legal_document()
    time.sleep(10)
    a.POST__api_tutorial_get_tutorial_gacha()
    time.sleep(10)
    a.POST__api_tutorial_fxm_tutorial_gacha_drawn_result()
    time.sleep(14)
    a.POST__api_tutorial_fxm_tutorial_gacha_exec()
    time.sleep(10)
    a.get_migrate_information("wtf")
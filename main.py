import logging
import sys
from api import API

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
    a.POST__api_tutorial_agree_legal_document()
    a.POST__api_tutorial_get_tutorial_gacha()
    a.POST__api_tutorial_fxm_tutorial_gacha_drawn_result()

    a.POST__api_tutorial_fxm_tutorial_gacha_exec()
    a.get_migrate_information("wtf")
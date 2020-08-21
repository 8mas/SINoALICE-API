import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.PlayerInformation import PlayerInformation
from bot.Bot import Bot

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("sinoalice.log", "w", "utf-8")
file_handler.setLevel(logging.DEBUG) # Set to info

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG) # Set to info

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

def reroll_good_account():
    no_good_account = True
    while no_good_account:
        bot = Bot()
        bot.create_new_account()
        bot.get_all_presents()
        bot.play_gacha(23)
        if(bot.is_good_account()):
            bot.migrate()
            no_good_account = False
            player_info = bot.api.player_information

    return player_info


def create_good_accounts():
    db_name = "sinoalice_accounts.db"
    PlayerInformation.create_db(db_name)
    engine = create_engine(f"sqlite:///{db_name}")
    Session = sessionmaker(bind=engine)
    session = Session()

    future_list = []
    with ThreadPoolExecutor(max_workers=1) as executor:
        for _ in range(10):
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


if __name__ == "__main__":
    create_good_accounts()
    logging.info("Finished")
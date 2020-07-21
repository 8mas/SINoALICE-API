import json
from pathlib import Path

base_path = Path(__file__).parent

def parse_card_en():
    file = open(base_path / "../resources/raw_resources/card_en.json", encoding="utf-8")
    data = file.read()
    data_dict = json.loads(data)

    better_dict = {}
    for json_data in data_dict:
        id = json_data["cardMstId"]
        better_dict[id] = {}
        better_dict[id]["rarity"] = json_data["rarity"]
        better_dict[id]["name"] = json_data["shortName"]
        better_dict[id]["cardType"] = json_data["cardType"]

    to_write = json.dumps(better_dict, indent=4)

    file = open(base_path / "../resources/card_en_parsed.json", "w")
    file.write(to_write)


def parse_character():
    file = open(base_path / "../resources/raw_resources/character.json", encoding="utf-8")
    data = file.read()
    data_dict = json.loads(data)

    better_dict = {}
    for json_data in data_dict:
        id = json_data["characterMstId"]
        better_dict[id] = {}
        better_dict[id]["name"] = json_data["name"]

    to_write = json.dumps(better_dict, indent=4)

    file = open(base_path / "../resources/character_parsed.json", "w")
    file.write(to_write)

parse_card_en()
parse_character()

with open(base_path / "../resources/character_parsed.json", "r") as character_file:
    data = character_file.read()
    character_dict = json.loads(data)


with open(base_path / "../resources/card_en_parsed.json", "r") as card_file:
    data = card_file.read()
    card_dict = json.loads(data)

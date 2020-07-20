import json


def parse_card_en():
    file = open("../resources/card_en.json", encoding="utf-8")
    data = file.read()
    data_dict = json.loads(data)

    better_dict = {}
    for json_data in data_dict:
        id = json_data["cardMstId"]
        better_dict[id] = {}
        better_dict[id]["rarity"] = json_data["rarity"]
        better_dict[id]["name"] = json_data["shortName"]

    to_write = json.dumps(better_dict, indent=4)

    file = open("../resources/card_en_parsed.json", "w")
    file.write(to_write)


def parse_character():
    file = open("../resources/character.json", encoding="utf-8")
    data = file.read()
    data_dict = json.loads(data)

    better_dict = {}
    for json_data in data_dict:
        id = json_data["characterMstId"]
        better_dict[id] = {}
        better_dict[id]["name"] = json_data["name"]

    to_write = json.dumps(better_dict, indent=4)

    file = open("../resources/character_parsed.json", "w")
    file.write(to_write)



# Todo better farm logic
class FarmLogic:
    TUTORIAL_RULES = 0
    GACHA_RULES = 1
    ACCOUNT_RULES = 2

    # Idea: make rules close to boolean logic: (id1 and id2 and id3) OR (id1, id4) = [(id1, id2, id3), (id1, id4)]
    tutorial_rules = []
    gacha_rules = []
    account_rules = []
    all_rules = [tutorial_rules, gacha_rules, account_rules]

    def add_rule(self, rule_set=ACCOUNT_RULES):
        # add rule to set without overwriting
        pass

    def is_good_tutorial_result(self, item_ids: list) -> bool:
        pass

    def is_good_gacha_result(self, item_ids: list) -> bool:
        pass

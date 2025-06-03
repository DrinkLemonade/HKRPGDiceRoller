import random
import logging
import copy

class Pawn:
    def __init__(self, name, attack, hp, shell):
        self.name = name
        self.attack = attack
        self.weapon = Weapon()
        self.armor = None
        self.hp = hp
        self.shell = shell

class Item:
    def __init__(self, id = "ITEM_ID", name = "Default Item", bulk = 1):
        self.id = id
        self.name = name
        self.bulk = bulk

class Weapon(Item):
    def __init__(self, id = "WEAPON_ID", name = "Default Weapon", damage = 0):
        # Inherit the methods and properties from the parent
        super().__init__(name)
        self.id = id
        self.name = name
        self.damage = damage

class Armor(Item):
    def __init__(self, id = "ARMOR_ID", name = "Default Armor", dr = 0, soak = 0, soak_reroll = 0):
        super().__init__(name)
        self.id = id
        self.name = name
        self.dr = dr
        self.soak = soak
        self.soak_reroll = soak_reroll

# We're taking advantage of Python's type-flexible (?) arrays and shoving everything into the same DB.
class DB:
    def __init__(self):
        self.contents = []
        self.contents.append(Weapon("WEAPON_DEBUG_NO_EFFECT", "Debug Weapon", damage = 2))
        self.contents.append(Weapon("WEAPON_NAIL", "Nail", damage = 2))
    
    def find(self, id, check_type = None):
        for item in self.contents:
            if (check_type == None or isinstance(item, check_type)) and item.id == id:
                return item
        return None
        
def roll_attack(attack_dice, target_number=5, deadeye=False):
    """Roll attack dice and count successes."""
    successes = roll_dice(attack_dice, target_number, count_sixes = deadeye)
    return successes

def soak_roll(soak_dice, damage):
    """Roll Soak dice and reduce damage."""
    successes = roll_dice(num_dice = soak_dice)
    final_damage = max(0, damage - successes)
    return final_damage

def roll_dice(num_dice, target_number=5, count_sixes=False, reroll_count=0):
    """Roll a number of dice and count successes, allowing rerolls of the lowest dice."""
    rolls = [random.randint(1, 6) for _ in range(num_dice)]
    rolls.sort()  # Sort the rolls in ascending order

    successes = sum(1 for roll in rolls if roll >= target_number)
    if count_sixes:
        successes += sum(1 for roll in rolls if roll == 6)

    # Reroll the specified number of lowest dice
    # By default, we only use the new roll if it's better.
    for i in range(reroll_count):
        if rolls[i] == 6:
            continue
        new_roll = random.randint(1, 6)
        if new_roll >= target_number:
            successes += 1
        if count_sixes and new_roll == 6:
            successes += 1
        rolls[i] = new_roll  # Replace the lowest roll with the new roll

    logger.debug(f"{rolls} - {successes} successes")
    return successes


def simulate_battle(num_battles, pawn_template_1, pawn_template_2, override_p1_attack = 0, override_p1_damage = 0, use_deadeye=False, use_guard_breaker=False):
    """Simulate a battle between two pawns and track average damage per turn."""
    total_turns = 0
    total_damage = 0

    for _ in range(num_battles):
        # A deep copy's objects are also copies of the original's objects, rather than references to them.
        pawn1 = copy.deepcopy(pawn_template_1)
        pawn2 = copy.deepcopy(pawn_template_2)

        if override_p1_attack > 0:
            pawn1.attack = override_p1_attack
        if override_p1_damage > 0:
            pawn1.weapon.damage = override_p1_attack
  
        guard_breaker_modifier = 0

        while pawn1.hp > 0 and pawn2.hp > 0:
            # Pawn 1 attacks Pawn 2
            damage_taken = attack(pawn1, pawn2, 5 + guard_breaker_modifier, use_deadeye)
            pawn2.hp -= damage_taken

            total_damage += damage_taken
            if damage_taken > 0 and use_guard_breaker:
                guard_breaker_modifier = -1

            # Pawn 2 attacks Pawn 1
            damage_taken = attack(pawn2, pawn1, 5)
            pawn1.hp -= damage_taken

            total_turns += 1
        if pawn1.hp <= 0:
            logger.debug(f"{pawn2.name} wins!")
        else:
            logger.debug(f"{pawn1.name} wins!")

    average_damage_per_turn = total_damage / total_turns
    return average_damage_per_turn

def attack(attacker, defender, base_difficulty, use_deadeye=False):
    successes = roll_attack(attacker.attack, base_difficulty, use_deadeye)
    if successes > 0:
        damage_risk = min(attacker.weapon.damage + successes - 1, 2 * attacker.weapon.damage)
        logger.debug(f"{attacker.name} attacks {defender.name} with {attacker.weapon.name}! {successes} successes, {damage_risk} damage risk.")

        armor_soak = 0
        # TODO add armor rerolls
        dr_text = ""
        soak_text = ""
        
        if defender.armor != None:
            dr = defender.armor.dr
            armor_soak = defender.armor.soak
            # Apply DR, which can't reduce risk below 1
            pre_dr_risk = damage_risk
            damage_risk = max(damage_risk - dr, 1)
            if damage_risk < pre_dr_risk:
                dr_text = f"(damage: {pre_dr_risk} to {damage_risk} after DR)"

        pre_soak_risk = damage_risk
        damage_risk = soak_roll(defender.shell + armor_soak, damage_risk)
        if damage_risk < pre_soak_risk:
            soak_text = f"(damage: from {pre_soak_risk} to {damage_risk} after Soak)"
            
        logger.debug(f"{damage_risk} damage! New health is {defender.hp}. {dr_text} {soak_text}")
        return damage_risk
    else:
        logger.debug(f"{attacker.name}'s attack misses {defender.name}.")
        return 0

###### MAIN ######
# Logging: DEBUG = Detailed info, INFO = Working as intended, WARNING = Unexpected, ERROR = Didn't work, CRITICAL = Could stop
# TODO check difference between logger and console handler!

# create logger
logger = logging.getLogger('DiceLogger')

# create console handler and set level to debug
ch = logging.StreamHandler()

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

#Prepare Simulation
result_list = []

#Simulation Settings
num_battles = 1
debug_level = logging.DEBUG # logging.INFO

logger.setLevel(debug_level)
ch.setLevel(debug_level)

# P1's attack dice count doesn't matter since we're overriding it to test ranges from 1 to 7.
content_db = DB()

pawn1 = Pawn("Beetle", attack = 3, hp = 10, shell = 3)
pawn1.weapon = content_db.find("WEAPON_NAIL")

pawn2 = Pawn("Ant", attack = 1, hp = 8, shell = 3)
pawn2.weapon = content_db.find("WEAPON_NAIL")

override_p1_attack = 0
override_p1_damage = 0


# Reminder: range's last value is not inclusive
for simulate_damage in range(1, 5):
    for simulate_attack in range (1, 8):
        average_damage = simulate_battle(num_battles, pawn1, pawn2, override_p1_attack, override_p1_damage)
        result_text = f"Average damage per attack for {simulate_attack} attack dice and {simulate_damage} damage: {average_damage:.2f}"
        result_list.append(result_text)


for i, result in enumerate(result_list, start=1):
    print(result)

input("Press Enter to exit...")

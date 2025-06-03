import random
import logging
import copy

# TODO LIST
# Implement light armor's soak rerolls
# Logging: DEBUG = Detailed info, INFO = Working as intended, WARNING = Unexpected, ERROR = Didn't work, CRITICAL = Could stop
# Check difference between logger and console handler!

# Item
class Item:
    def __init__(self, id="ITEM_DEBUG_PLACEHOLDER", name="Debug Placeholder Item", bulk=1):
        self.id = id
        self.name = name
        self.bulk = bulk

# Weapon
class Weapon(Item):
    def __init__(self, id="WEAPON_DEBUG_PLACEHOLDER", name="Debug Placeholder Weapon", damage=0):
        super().__init__(name)
        self.id = id
        self.name = name
        self.damage = damage

# Armor
class Armor(Item):
    def __init__(self, id="ARMOR_DEBUG_PLACEHOLDER", name="Debug Placeholder Armor", dr=0, soak=0, soak_reroll=0):
        super().__init__(name)
        self.id = id
        self.name = name
        self.dr = dr
        self.soak = soak
        self.soak_reroll = soak_reroll

# Dice
class Dice:
    @staticmethod
    def roll_attack(attack_dice, target_number=5, deadeye=False):
        """Roll attack dice and count successes."""
        successes = Dice.roll_dice(attack_dice, target_number, count_sixes=deadeye)
        return successes

    @staticmethod
    def roll_soak(soak_dice, damage):
        """Roll Soak dice and reduce damage."""
        successes = Dice.roll_dice(num_dice=soak_dice)
        final_damage = max(0, damage - successes)
        return final_damage

    @staticmethod
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

# Pawn
class Pawn:
    def __init__(self, name, attack, hp, shell, weapon, armor):
        self.name = name
        self.attack = attack
        self.hp = hp
        self.shell = shell
        self.weapon = weapon
        self.armor = armor

    def attack_target(self, target, base_difficulty, use_deadeye=False):
        successes = Dice.roll_attack(self.attack, base_difficulty, use_deadeye)
        if successes > 0:
            damage_risk = min(self.weapon.damage + successes - 1, 2 * self.weapon.damage)
            logger.debug(f"{self.name} attacks {target.name} with {self.weapon.name}! {successes} successes, {damage_risk} damage risk.")

            damage_risk = self.apply_armor_and_soak(target, damage_risk)
            return damage_risk
        else:
            logger.debug(f"{self.name}'s attack misses {target.name}.")
            return 0

    def apply_armor_and_soak(self, target, damage_risk):
        if target.armor:
            # Apply DR, which can't reduce risk below 1
            pre_dr_risk = damage_risk
            damage_risk = max(damage_risk - target.armor.dr, 1)
            if damage_risk < pre_dr_risk:
                logger.debug(f"(damage: {pre_dr_risk} to {damage_risk} after DR)")

        pre_soak_risk = damage_risk
        damage_risk = Dice.roll_soak(target.shell + (target.armor.soak if target.armor else 0), damage_risk)
        if damage_risk < pre_soak_risk:
            logger.debug(f"(damage: from {pre_soak_risk} to {damage_risk} after Soak)")

        return damage_risk

# DB
class DB:
    def __init__(self):
        self.contents = []
        self.contents.append(Weapon("WEAPON_DEBUG_NO_EFFECT", "Debug Weapon", damage=2))
        self.contents.append(Weapon("WEAPON_NAIL", "Nail", damage=2))

        self.contents.append(Armor("ARMOR_NONE", "No Armor"))
        self.contents.append(Armor("ARMOR_LIGHT", "Light Armor", soak=1, soak_reroll=1))
        self.contents.append(Armor("ARMOR_MEDIUM", "Medium Armor", soak=1, dr=1))
        self.contents.append(Armor("ARMOR_HEAVY", "Heavy Armor", soak=1, dr=2))

    def find(self, id, check_type=None):
        for item in self.contents:
            if (check_type is None or isinstance(item, check_type)) and item.id == id:
                return item
        return None

# Simulation
def simulate_battle(num_battles, pawn1, pawn2, use_deadeye=False, use_guard_breaker=False):
    total_turns = 0
    total_damage = 0

    for _ in range(num_battles):
        pawn1_copy = copy.deepcopy(pawn1)
        pawn2_copy = copy.deepcopy(pawn2)

        guard_breaker_modifier = 0

        while pawn1_copy.hp > 0 and pawn2_copy.hp > 0:
            # Pawn 1 attacks Pawn 2
            damage_taken = pawn1_copy.attack_target(pawn2_copy, 5 + guard_breaker_modifier, use_deadeye)
            pawn2_copy.hp -= damage_taken
            logger.debug(f"{damage_taken} damage! New health is {pawn2_copy.hp}.")


            total_damage += damage_taken
            if damage_taken > 0 and use_guard_breaker:
                guard_breaker_modifier = -1

            # Pawn 2 attacks Pawn 1            
            damage_taken = pawn2_copy.attack_target(pawn1_copy, 5)
            pawn1_copy.hp -= damage_taken

            total_turns += 1

        if pawn1_copy.hp <= 0:
            logger.debug(f"{pawn2.name} wins!")
        else:
            logger.debug(f"{pawn1.name} wins!")

    average_damage_per_turn = total_damage / total_turns
    return average_damage_per_turn

def simulation_cycle(pawn1, pawn2, debug_level=logging.INFO):
    logger.setLevel(debug_level)
    ch.setLevel(debug_level)
    result_list = []  # Clear results

    average_damage = simulate_battle(num_battles, pawn1, pawn2)
    result_text = f"Over {num_battles} battles, with Pawn 1's {pawn1.weapon.damage} damage {pawn1.weapon.name} rolling {pawn1.attack} dice against Pawn 2's {pawn2.shell} Shell and {pawn2.armor.name}, Pawn 1's average damage per attack is: {average_damage:.2f}"

    return result_text

# Logging
logger = logging.getLogger('DiceLogger')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Prepare Simulation
content_db = DB()

# Simulation Settings
pawn1 = Pawn("Beetle", attack=6, hp=10, shell=3, weapon=content_db.find("WEAPON_NAIL"), armor=content_db.find("ARMOR_NONE"))
pawn2 = Pawn("Ant", attack=1, hp=8, shell=3, weapon=content_db.find("WEAPON_NAIL"), armor=content_db.find("ARMOR_NONE"))

# Run Simulations
num_battles = 1
print("Running a single, detailed battle simulation...")
print(simulation_cycle(pawn1, pawn2, logging.DEBUG))

num_battles = 300
print("From now on, we run each simulation 300 times and don't check the details.")
print(simulation_cycle(pawn1, pawn2))

print("\nLet's give the second bug armor this time.")
pawn2.armor = content_db.find("ARMOR_MEDIUM")
print(simulation_cycle(pawn1, pawn2))

print("\nRunning several sets of simulations now, each overriding Pawn 1's attack dice count with a new value.")
pawn2.armor = content_db.find("ARMOR_NONE")

test_p1_attack_min = 2
test_p1_attack_max = 7
test_p1_damage_min = 1
test_p1_damage_max = 3

for i in range(test_p1_damage_min, test_p1_damage_max+1):
    pawn1.weapon.damage = i
    for j in range(test_p1_attack_min, test_p1_attack_max+1):
        pawn1.attack = j
        print(simulation_cycle(pawn1, pawn2))

input("Press Enter to exit...")

import random

class Bug:
    def __init__(self, name, attack, damage, hp, shell):
        self.name = name
        self.attack = attack
        self.damage = damage
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

class ItemDB:
    def __init__(self):
        self.contents = []
        contents.append(Weapon("WEAPON_NAIL", "Nail", damage = 2))
        
        
def roll_attack(attack_dice, target_number=5, deadeye=False):
    """Roll attack dice and count successes."""
    successes = roll_dice(attack_dice, target_number, count_sixes = deadeye)
    return successes

def determine_damage(soak_dice, damage):
    """Roll shell dice and reduce damage."""
    shell_rolls = [random.randint(1, 6) for _ in range(soak_dice)]
    shell_successes = sum(1 for roll in shell_rolls if roll >= 5)
    final_damage = max(0, damage - shell_successes)
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

    return successes


def simulate_battle(num_battles, atk_dice, atk_dmg, use_deadeye=False, use_guard_breaker=False):
    """Simulate a battle between two bugs and track average damage per turn."""
    total_turns = 0
    total_damage = 0

    for _ in range(num_battles):
        bug1 = Bug("Beetle", attack = atk_dice, damage = atk_dmg, hp = 10, shell = 3)
        bug2 = Bug("Ant", attack = 1, damage = 1, hp = 8, shell = 3)

        guard_breaker_modifier = 0

        while bug1.hp > 0 and bug2.hp > 0:
            # Bug 1 attacks Bug 2
            damage_taken = attack(bug1, bug2, 5 + guard_breaker_modifier, use_deadeye)
            total_damage += damage_taken
            if damage_taken > 0 and use_guard_breaker:
                guard_breaker_modifier = -1

            # Bug 2 attacks Bug 1
            damage_taken = attack(bug2, bug1, 5)

            total_turns += 1
        if bug1.hp <= 0:
            print(f"{bug2.name} wins!")
        else:
            print(f"{bug1.name} wins!")

    average_damage_per_turn = total_damage / total_turns
    return average_damage_per_turn

def attack(attacker, defender, base_difficulty, use_deadeye=False):
    successes = roll_attack(attacker.attack, base_difficulty, use_deadeye)
    if successes > 0:
        damage_risk = min(attacker.damage + successes - 1, 2 * attacker.damage)
        damage_taken = determine_damage(defender.shell, damage_risk)
        defender.hp -= damage_taken
        print(f"{attacker.name} attacks {defender.name} and deals {damage_taken} damage.")
        return damage_taken
    else:
        print(f"{attacker.name}'s attack misses {defender.name}.")
        return 0

# Example usage
result_list = []
num_battles = 300

# Reminder: range's last value is not inclusive
for simulate_damage in range(1, 5):
    for simulate_attack in range (1, 8):
        average_damage = simulate_battle(num_battles, simulate_attack, simulate_damage)
        result_text = f"Average damage per attack for {simulate_attack} attack dice and {simulate_damage} damage: {average_damage:.2f}"
        result_list.append(result_text)


for i, result in enumerate(result_list, start=1):
    print(result)

input("Press Enter to exit...")
import re
import random
import math



class Die:
    def __init__(self, notation):
        self.dice_count, self.dice_sides = self.parse_notation(notation)

    def parse_notation(self, notation):
        if 'd' in notation:
            dice_count, dice_sides = notation.split('d')
            return int(dice_count), int(dice_sides)
        else:
            raise ValueError("Invalid dice notation")

    def roll(self):
        return sum(random.randint(1, self.dice_sides) for _ in range(self.dice_count))


class Roll:
    def __init__(self, roll_notation):
        self.rolls = self.parse_roll_notation(roll_notation)

    def parse_roll_notation(self, notation):
        notation = '+' + notation
        pattern = r'[+-][^+-]+'
        matches = re.findall(pattern, notation)

        processed_rolls = []
        for match in matches:
            operator, roll = match[0], match[1:]
            processed_rolls.append((operator, roll))
        return processed_rolls

    def get_outcome(self):
        total = 0
        for operator, roll in self.rolls:
            if 'd' in roll:
                advantage = '^' in roll
                disadvantage = 'v' in roll
                if advantage == disadvantage:
                    advantage, disadvantage = False, False
                #assumes that v/^ is at the end of the dice roll. also 2d20^ will be higher roll between 2d20 and 2d20
                roll = roll[:-1] if (advantage or disadvantage) else roll 
                die = Die(roll)
                if advantage:
                    roll_result = max(die.roll(), die.roll())
                elif disadvantage: #remember about elif
                    roll_result = min(die.roll(), die.roll())
                else:
                    roll_result = die.roll()
            else:
                roll_result = int(roll)
            
            if operator == '+':
                total += roll_result
            else:  # operator is '-'
                total -= roll_result
        return total



class Character:
    def __init__(self, name, level, ability_scores, health, attacks, spells, hostile):
        self.name = name
        self.level = level
        self.ability_scores = ability_scores
        
        self.health = health
        self.attacks = attacks
        self.spells = spells
        self.initiative = 0
        self.hostile = hostile
        self.concentration = False

        self.ability_modifiers = self.calculate_ability_modifiers(self.ability_scores)
        self.armor_class = 10 + self.ability_modifiers['dex']
        self.proficiency_bonus = math.floor((self.level-1)/4)+2


    def calculate_ability_modifiers(self, ability_scores):
        ability_modifiers = {ability: (lambda score: math.floor((score - 10) / 2))(score) for ability, score in ability_scores.items()}
        return ability_modifiers
        

    def take_damage(self, damage):
        self.health -= damage
        print(f"{self.name} takes {damage} damage. Remaining health: {self.health}")

    def heal_damage(self, damage):
        self.health += damage
        print(f"{self.name} healed from {damage} damage. Remaining health: {self.health}")

    def is_alive(self):
        return self.health > 0

    def attack(self, target):
        for attack in self.attacks:
            attack.execute(self, target)

    def cast_spell(self, spell_name, target):
        for spell in self.spells:
            if spell.name == spell_name:
                spell.cast(target)


class Attack:
    def __init__(self, name, roll_notation, attack_ability):
        self.name = name
        self.damage_roll = Roll(roll_notation)
        self.attack_roll = Roll('1d20')
        self.attack_ability = attack_ability

    def execute(self, attacker, target):
        attack_modifier = attacker.ability_modifiers[self.attack_ability] + attacker.proficiency_bonus
        attack_roll = self.attack_roll.get_outcome() + attack_modifier
        print(f'{self.name} attack roll: {attack_roll}')
        if attack_roll >= target.armor_class:
            damage = self.damage_roll.get_outcome()+attack_modifier
            print(f"{self.name} attack! Damage: {damage}")
            target.take_damage(damage)
        else:
            print(f"{self.name} misses {target.name}!")


class Spell:
    def __init__(self, name, roll_notation):
        self.name = name
        self.roll = Roll(roll_notation)

    def cast(self, target):
        damage = self.roll.get_outcome()
        print(f"Casting {self.name}! Damage: {damage}")
        target.take_damage(damage)


class CombatManager:
    def __init__(self, characters):
        self.characters = characters
        self.roll = Roll('1d20')
        for character in characters:
            character.initiative = self.roll.get_outcome()+character.ability_modifiers['dex']
            print(f"{character.name} initiative: {character.initiative}")
        self.initiative_order = sorted(characters, key=lambda x: x.initiative, reverse=True)

    def combat_round(self):
        for character in self.initiative_order:
            if character.is_alive():
                print(f"\n{character.name}'s turn:")
                #logic for selecting an action, but I have to improve this later
                if character.spells:
                    target = self.select_target(character)
                    if target:
                        character.cast_spell(character.spells[0].name, target)
                elif character.attacks:
                    target = self.select_target(character)
                    if target:
                        character.attack(target)

        # Check if all characters in one group are defeated
        hostiles_alive = any(c.is_alive() and c.hostile for c in self.initiative_order)
        non_hostiles_alive = any(c.is_alive() and not c.hostile for c in self.initiative_order)
        
        #end/continue combat
        if not hostiles_alive or not non_hostiles_alive:
            return False  
        return True

    def select_winning_side(self):
        hostiles_alive = any(c.is_alive() and c.hostile for c in self.initiative_order)
        non_hostiles_alive = any(c.is_alive() and not c.hostile for c in self.initiative_order)

        if hostiles_alive and not non_hostiles_alive:
            return 'hostiles'
        elif not hostiles_alive and non_hostiles_alive:
            return 'non-hostiles'

    def select_target(self, attacker):
        for character in self.initiative_order:
            if character.is_alive() and character.hostile != attacker.hostile:
                return character
        return None
    

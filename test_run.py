
from dnd_classes import Character, Spell, Attack, Die, Roll, CombatManager

# Initialize characters and combat manager
hero = Character("Hero",
                {'str':6, 'dex':10, 'con':10, 'int': 10, 'wis': 10, 'cha':10},50,[],[Spell("Holy Smite", '4d4')],False)
skeleton = Character("Skeleton",
                    {'str':10, 'dex':10, 'con':10, 'int': 10, 'wis': 10, 'cha':10},20,[Attack("Melee", '3d4','str')],[], True)
zombie = Character("Zombie",
                   {'str':10, 'dex':10, 'con':10, 'int': 10, 'wis': 10, 'cha':10},15,[Attack("Claw", '1d4','str')],[],True)

characters = [hero,skeleton, zombie, zombie, zombie]

def run_combat(characters):
    combat_manager = CombatManager(characters)
    while True:
        if not combat_manager.combat_round():
            break
    winning_side = combat_manager.select_winning_side()
    return winning_side

N=500
lever = True


import os
import sys
from contextlib import contextmanager
import itertools

if lever:
    N = 1
    print(f"winning side: {run_combat(characters)}")
else:
    @contextmanager
    def suppress_print():
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            yield
        finally:
            sys.stdout.close()
            sys.stdout = original_stdout


    with suppress_print():
        winner=[]
        dex=[]
        dice=[]
        health=[]
        for X, Y, Z, N in itertools.product(range(1, 11), range(1, 11), range(1,10), range(N)):
            hero = Character("Hero",
                {'str':6, 'dex':10, 'con':10, 'int': 10, 'wis': 10, 'cha':10},50,[],[Spell("Holy Smite", '4d4')],False)
            skeleton = Character("Skeleton",
                {'str':10, 'dex':8+Y, 'con':10, 'int': 10, 'wis': 10, 'cha':10},20+Z,[Attack("Melee", f'{X}d4','str')],[], True)
            characters = [hero,skeleton]
            winner.append(run_combat(characters))
            dex.append(8+Y)
            dice.append(X)
            health.append(Z)
        
        import pandas as pd
        dict = {'winner':winner, 'dex':dex, 'dice':dice, 'health':health}
        df = pd.DataFrame(dict)
        df.to_csv('results.csv')
        print('results save to results.csv file.')


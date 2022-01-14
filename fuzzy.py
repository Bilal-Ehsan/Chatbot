from colorama import Fore
from simpful import *

import bot


FS = FuzzySystem(show_banner=False)  # Fuzzy system object

with open('fuzzy_rules.txt') as f:
    rules = [rule.rstrip() for rule in f]
FS.add_rules(rules)

S_1 = FuzzySet(function=Triangular_MF(a=0, b=0, c=5), term='weak')
S_2 = FuzzySet(function=Triangular_MF(a=0, b=5, c=10), term='average')
S_3 = FuzzySet(function=Triangular_MF(a=5, b=10, c=10), term='high')
FS.add_linguistic_variable('Strength', LinguisticVariable([S_1, S_2, S_3], concept='How strong', universe_of_discourse=[0,10]))

F_1 = FuzzySet(function=Triangular_MF(a=0, b=0, c=10), term='slow')
F_2 = FuzzySet(function=Triangular_MF(a=0, b=10, c=10), term='rapid')
FS.add_linguistic_variable('Speed', LinguisticVariable([F_1, F_2], concept='How fast', universe_of_discourse=[0,10]))

T_1 = FuzzySet(function=Triangular_MF(a=0, b=0, c=10), term='low')
T_2 = FuzzySet(function=Triangular_MF(a=0, b=10, c=20), term='medium')
T_3 = FuzzySet(function=Trapezoidal_MF(a=10, b=20, c=25, d=25), term='high')
FS.add_linguistic_variable('Threat', LinguisticVariable([T_1, T_2, T_3], universe_of_discourse=[0,25]))


def character_threat_calculator():
    character = input('\nWho is your character? ')
    service = input('From 0-10, how strong is your character? ')
    food = input('From 0-10, how fast is your character? ')

    FS.set_variable('Strength', int(service))
    FS.set_variable('Speed', int(food))
    result = FS.Mamdani_inference(['Threat'])

    threat = result.get('Threat')
    if threat >= 0 and threat < 12:
        print(f'\n{Fore.LIGHTMAGENTA_EX}{character} is not a threat at all...\n')
        bot.speak(f'{character} is not a threat at all...')
    elif threat >= 12 and threat < 14:
        print(f'\n{Fore.LIGHTMAGENTA_EX}{character} is somewhat of a threat.\n')
        bot.speak(f'{character} is somewhat of a threat.')
    elif threat >= 14 and threat < 16:
        print(f'\n{Fore.LIGHTMAGENTA_EX}{character} is definitely a threat!\n')
        bot.speak(f'{character} is definitely a threat!')
    elif threat >= 16 and threat < 18:
        print(f'\n{Fore.LIGHTMAGENTA_EX}{character} is a super threat!!\n')
        bot.speak(f'{character} is a super threat!!')
    else:
        print(f'\n{Fore.LIGHTMAGENTA_EX}{character} is a god-level threat!!!\n')
        bot.speak(f'{character} is a god-level threat!!!')

from colorama import Fore
from nltk.sem import Expression
from nltk.inference import ResolutionProver

import bot


read_expr = Expression.fromstring

kb = []
with open('knowledge_base.txt', 'r') as f:
    for line in f:
        stripped = line.strip()
        if stripped:
            kb.append(read_expr(stripped))


def integrity_check():
    test_kb = kb.copy()
    test_inputs = [
        read_expr('-Evil(Superman)'),
        read_expr('-Human(Groot)'),
        read_expr('Avenger(Tony)'),
        read_expr('Avenger(Steve)'),
        read_expr('Avenger(Natasha)'),
        read_expr('Avenger(Bruce)'),
        read_expr('Avenger(Thor)'),
        read_expr('Avenger(Clint)'),
        read_expr('Enemies(Zod, Superman)')
    ]

    for i in range(len(test_inputs)):
        result = ResolutionProver().prove(test_inputs[i], test_kb)
        if result:
            test_kb.append(test_inputs[i])
        else:
            print(Fore.LIGHTRED_EX + '\nInternal contradiction found! Exiting system...')
            quit()   


def add_to_kb(q):
    if 'and' in q:
        object_1, object_2 = q.split(' and ')
        expr = read_expr(f'Enemies({object_1.capitalize()}, {object_2.capitalize()})')
    else:
        object, subject = q.split(' is ')
        expr = read_expr(f'{subject.capitalize()}({object.capitalize()})')

    if expr in kb:
        print(Fore.LIGHTMAGENTA_EX + 'I already knew that!')
        bot.speak('I already knew that!')
        return

    result = ResolutionProver().prove(expr, kb)
    if result:
        kb.append(expr)
        print(Fore.LIGHTMAGENTA_EX + 'Okay, I\'ll remember that!')
        bot.speak('Okay, I\'ll remember that!')
    else:
        print(Fore.LIGHTMAGENTA_EX + 'Sorry, that contradicts with what I know!')
        bot.speak('Sorry, that contradicts with what I know!')


def fact_check(fact):
    if fact in kb:
        print(Fore.LIGHTMAGENTA_EX + 'Incorrect')
        bot.speak('Incorrect')


def is_in_kb(expr):
    if expr not in kb:
        print(Fore.LIGHTMAGENTA_EX + 'There\'s nothing about this in my knowledge base!')
        bot.speak('There\'s nothing about this in my knowledge base!')
        return False
    return True


def is_multi_valued_in_kb(expr):
    if expr not in kb:
        return False
    return True


def check_kb(q):
    if 'not' in q:
        object, subject = q.split(' is not ')
        expr = read_expr(f'-{subject.capitalize()}({object.capitalize()})')
        if not is_in_kb(expr): return
    elif 'and' in q:
        object_1, object_2 = q.split(' and ')
        expr = read_expr(f'Enemies({object_1.capitalize()}, {object_2.capitalize()})')
        second_expr = read_expr(f'Enemies({object_2.capitalize()}, {object_1.capitalize()})')
        
        in_kb = (not is_multi_valued_in_kb(expr)) and (not is_multi_valued_in_kb(second_expr))
        if in_kb:
            print(Fore.LIGHTMAGENTA_EX + 'There\'s nothing about this in my knowledge base!')
            bot.speak('There\'s nothing about this in my knowledge base!')
            return
    else:
        object, subject = q.split(' is ')
        expr = read_expr(f'{subject.capitalize()}({object.capitalize()})')
        if not is_in_kb(expr): return

    result = ResolutionProver().prove(expr, kb)
    if result:
        print(Fore.LIGHTMAGENTA_EX + 'That\'s correct!')
        bot.speak('That\'s correct!')
    else:
        print('I\'m not sure about that... Let me check...')

        if 'is evil' in q:
            fact_to_check = read_expr(f'Superhero({object.capitalize()})')
            fact_check(fact_to_check)
        elif 'is human' in q:
            fact_to_check = read_expr(f'Alien({object.capitalize()})')
            fact_check(fact_to_check)
        elif subject == 'Avenger' or subject == 'avenger':
            fact_to_check = read_expr(f'Marvel({object.capitalize()})')
            if fact_to_check not in kb:
                print(Fore.LIGHTMAGENTA_EX + 'Sorry, I don\'t know')
                bot.speak('Sorry, I don\'t know')
        elif object == 'Kryptonite' or object == 'kryptonite':
            print(Fore.LIGHTMAGENTA_EX + 'Incorrect')
            bot.speak('Incorrect')

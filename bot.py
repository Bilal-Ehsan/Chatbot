import json
import requests
import os
import random
import webbrowser

import aiml
import colorama
from colorama import Fore
from dotenv import load_dotenv
from nltk.sem import Expression
from nltk.inference import ResolutionProver
import pyttsx3
from simpful import *
import wikipedia

import similarity
import fuzzy


load_dotenv()
engine = pyttsx3.init()
colorama.init(autoreset=True)
read_expr = Expression.fromstring

# The Kernel object is the public interface to the AIML interpreter
kern = aiml.Kernel()
kern.setTextEncoding(None)

kb = []
with open('knowledge_base.txt', 'r') as f:
    for line in f:
        stripped = line.strip()
        if stripped:
            kb.append(read_expr(stripped))

with open('fuzzy_rules.txt') as f:
    rules = [rule.rstrip() for rule in f]
fuzzy.FS.add_rules(rules)


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


def speak(text):
    engine.say(text)
    engine.runAndWait()


def show_prompts():
    print(Fore.LIGHTCYAN_EX + '\nTry asking...\n')
    print('Show me the stats of [superhero]')
    print('Show me a picture of [superhero]')
    print('Show me a picture of a random superhero')
    print('Character threat calculator\n')


def wikipedia_search(params):
    try:
        summary = wikipedia.summary(params[1], sentences=3, auto_suggest=False)
        print(summary)
    except:
        print(Fore.LIGHTRED_EX + 'Sorry, I do not know that. Be more specific!')


def get_weather(params):
    succeeded = False
    api_url = r'http://api.openweathermap.org/data/2.5/weather?q='
    response = requests.get(api_url + params[1] + (r'&units=metric&APPID='+
                            os.getenv("WEATHER_API_KEY")))

    if response.status_code == 200:
        response_json = json.loads(response.content)
        if response_json:
            t = response_json['main']['temp']
            tmi = response_json['main']['temp_min']
            tma = response_json['main']['temp_max']
            hum = response_json['main']['humidity']
            wsp = response_json['wind']['speed']
            conditions = response_json['weather'][0]['description']
            print(f'The temperature is {t} °C, varying between {tmi} and {tma} at the' \
                f' moment, humidity is {hum} %, wind speed {wsp} m/s, {conditions}')
            succeeded = True
    if not succeeded:
        print(Fore.LIGHTRED_EX + 'Sorry, I could not resolve the location you gave me.')


def show_stats(superhero):
    try:
        response = requests.get(f'https://superheroapi.com/api/{os.getenv("SUPERHERO_API_KEY")}/search/{superhero}')
        if response.status_code == 200:
            response_json = json.loads(response.content)
            power_stats = response_json['results'][0]['powerstats']
            biography = response_json['results'][0]['appearance']
            work = response_json['results'][0]['work']
            print(f'{Fore.LIGHTCYAN_EX}-> {superhero} related info:\n')

            for x, y in power_stats.items():
                print(f'{x.capitalize()} - {y}')
            print()
            for x, y in biography.items():
                print(f'{x.capitalize()} - {y}')
            print()
            for x, y in work.items():
                print(f'{x.capitalize()} - {y}')
    except:
        print(f'{Fore.LIGHTRED_EX}Sorry, I couldn\'t find the stats of {superhero}!')


def show_image(superhero):
    if superhero == 'random':
        superhero_id = random.randint(1, 732)
        link = f'https://superheroapi.com/api/{os.getenv("SUPERHERO_API_KEY")}/{superhero_id}/image'
    else:
        link = f'https://superheroapi.com/api/{os.getenv("SUPERHERO_API_KEY")}/search/{superhero}'

    try:
        response = requests.get(link)
        if response.status_code == 200:
            response_json = json.loads(response.content)

            if superhero == 'random':
                image = response_json.get('url')
            else:
                image = response_json['results'][0]['image'].get('url')
            webbrowser.open(image)
    except:
        print(f'{Fore.LIGHTRED_EX}Sorry, I couldn\'t find a picture of {superhero}!')


def add_to_kb(q):
    if 'and' in q:
        object_1, object_2 = q.split(' and ')
        expr = read_expr(f'Enemies({object_1.capitalize()}, {object_2.capitalize()})')
    else:
        object, subject = q.split(' is ')
        expr = read_expr(f'{subject.capitalize()}({object.capitalize()})')

    if expr in kb:
        print(Fore.LIGHTMAGENTA_EX + 'I already knew that!')
        speak('I already knew that!')
        return

    result = ResolutionProver().prove(expr, kb)
    if result:
        kb.append(expr)
        print(Fore.LIGHTMAGENTA_EX + 'Okay, I\'ll remember that!')
        speak('Okay, I\'ll remember that!')
    else:
        print(Fore.LIGHTMAGENTA_EX + 'Sorry, that contradicts with what I know!')
        speak('Sorry, that contradicts with what I know!')


def fact_check(fact):
    if fact in kb:
        print(Fore.LIGHTMAGENTA_EX + 'Incorrect')
        speak('Incorrect')


def is_in_kb(expr):
    if expr not in kb:
        print(Fore.LIGHTMAGENTA_EX + 'There\'s nothing about this in my knowledge base!')
        speak('There\'s nothing about this in my knowledge base!')
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
            speak('There\'s nothing about this in my knowledge base!')
            return
    else:
        object, subject = q.split(' is ')
        expr = read_expr(f'{subject.capitalize()}({object.capitalize()})')
        if not is_in_kb(expr): return

    result = ResolutionProver().prove(expr, kb)
    if result:
        print(Fore.LIGHTMAGENTA_EX + 'That\'s correct!')
        speak('That\'s correct!')
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
                speak('Sorry, I don\'t know')
        elif object == 'Kryptonite' or object == 'kryptonite':
            print(Fore.LIGHTMAGENTA_EX + 'Incorrect')
            speak('Incorrect')


def character_threat_calculator():
    character = input('Who is your character? ')
    service = input('From 0-10, how strong is your character? ')
    food = input('From 0-10, how fast is your character? ')

    fuzzy.FS.set_variable('Strength', int(service))
    fuzzy.FS.set_variable('Speed', int(food))
    result = fuzzy.FS.Mamdani_inference(['Threat'])

    threat = result.get('Threat')
    if threat > 10 and threat < 12:
        print(f'\n{Fore.LIGHTMAGENTA_EX}{character} is not a threat at all...')
        speak(f'{character} is not a threat at all...')
    elif threat >= 12 and threat < 14:
        print(f'\n{Fore.LIGHTMAGENTA_EX}{character} is somewhat of a threat.')
        speak(f'{character} is somewhat of a threat.')
    elif threat >= 14 and threat < 16:
        print(f'\n{Fore.LIGHTMAGENTA_EX}{character} is definitely a threat!')
        speak(f'{character} is definitely a threat!')
    elif threat >= 16 and threat < 18:
        print(f'\n{Fore.LIGHTMAGENTA_EX}{character} is a super threat!!')
        speak(f'{character} is a super threat!!')
    else:
        print(f'\n{Fore.LIGHTMAGENTA_EX}{character} is a god-level threat!!!')
        speak(f'{character} is a god-level threat!!!')


def main():
    integrity_check()
    kern.bootstrap(learnFiles='patterns.xml')

    print(Fore.LIGHTGREEN_EX + 'Welcome to the chatbot! I like to talk about superheroes')
    print(Fore.LIGHTGREEN_EX + 'For a cool list of prompts, enter \'prompts\'!')

    while True:
        try:
            user_input = input('> ')
        except (KeyboardInterrupt, EOFError):
            print(Fore.LIGHTRED_EX + 'Uh oh... Something unexpected happened. Bye!')
            break

        # Pre-process user input and determine response agent (if needed)
        response_agent = 'aiml'
        # Activate selected response agent
        if response_agent == 'aiml':
            answer = kern.respond(user_input)  # Compute response
        # Post-process the answer for commands
        if answer[0] == '#':
            params = answer[1:].split('$')
            cmd = int(params[0])

            if cmd == 1:
                print(Fore.LIGHTMAGENTA_EX + params[1])
                speak(params[1])
                break
            elif cmd == 2:
                wikipedia_search(params)
            elif cmd == 3:
                get_weather(params)
            elif cmd == 4:
                show_prompts()
            elif cmd == 5:
                show_stats(params[1].strip())
            elif cmd == 6:
                show_image(params[1].strip())
            elif cmd == 7:
                show_image('random')
            elif cmd == 8:
                character_threat_calculator()
            elif cmd == 9:
                add_to_kb(params[1].strip())
            elif cmd == 10:
                check_kb(params[1].strip())
            elif cmd == 0:
                similarity.similarity_check(params[1].strip())
        else:
            print(Fore.LIGHTMAGENTA_EX + answer)
            speak(answer)


if __name__ == '__main__':
    main()

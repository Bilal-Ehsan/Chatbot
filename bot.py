import aiml
import colorama
from colorama import Fore
from dotenv import load_dotenv
from nltk.sem import Expression
from nltk.inference import ResolutionProver
import pyttsx3
from simpful import *

import fuzzy
import logic
import similarity
import web_services


load_dotenv()
engine = pyttsx3.init()
colorama.init(autoreset=True)

# The Kernel object is the public interface to the AIML interpreter
kern = aiml.Kernel()
kern.setTextEncoding(None)

with open('fuzzy_rules.txt') as f:
    rules = [rule.rstrip() for rule in f]
fuzzy.FS.add_rules(rules)


def speak(text):
    engine.say(text)
    engine.runAndWait()


def show_prompts():
    print(Fore.LIGHTCYAN_EX + '\nTry asking...\n')
    print('Show me the stats of [superhero]')
    print('Show me a picture of [superhero]')
    print('Show me a picture of a random superhero')
    print('Character threat calculator\n')


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
    logic.integrity_check()
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
                web_services.wikipedia_search(params)
            elif cmd == 3:
                web_services.get_weather(params)
            elif cmd == 4:
                show_prompts()
            elif cmd == 5:
                web_services.show_stats(params[1].strip())
            elif cmd == 6:
                web_services.show_image(params[1].strip())
            elif cmd == 7:
                web_services.show_image('random')
            elif cmd == 8:
                character_threat_calculator()
            elif cmd == 9:
                logic.add_to_kb(params[1].strip())
            elif cmd == 10:
                logic.check_kb(params[1].strip())
            elif cmd == 0:
                similarity.similarity_check(params[1].strip())
        else:
            print(Fore.LIGHTMAGENTA_EX + answer)
            speak(answer)


if __name__ == '__main__':
    main()

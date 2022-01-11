import aiml
import colorama
from colorama import Fore
from dotenv import load_dotenv
import pyttsx3
from simpful import *

import fuzzy
import similarity
import web_services


load_dotenv()
engine = pyttsx3.init()
colorama.init(autoreset=True)
read_expr = Expression.fromstring

# The Kernel object is the public interface to the AIML interpreter
kern = aiml.Kernel()
kern.setTextEncoding(None)


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
                fuzzy.character_threat_calculator()
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

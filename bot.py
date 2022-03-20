import aiml
import colorama
from colorama import Fore
from dotenv import load_dotenv
import pyttsx3

import azure_services
import fuzzy
import logic
import image_classification
import similarity
import web_services


load_dotenv()
engine = pyttsx3.init()
colorama.init(autoreset=True)

# The Kernel object is the public interface to the AIML interpreter
kern = aiml.Kernel()
kern.setTextEncoding(None)


def speak(text):
    engine.say(text)
    engine.runAndWait()


def show_prompts():
    print(Fore.LIGHTCYAN_EX + '\nTry asking...\n')
    print('Show me the stats of [character]')
    print('Show me a picture of [character]')
    print('Show me a picture of a random character')
    print('Character threat calculator')
    print('Classify image locally')
    print('Classify weapon using the cloud\n')


def main():
    logic.integrity_check()
    kern.bootstrap(learnFiles='patterns.xml')

    print(Fore.LIGHTGREEN_EX + 'Welcome to the chatbot! I like to talk about superheroes')
    print(Fore.LIGHTGREEN_EX + 'For a cool list of prompts, enter \'prompts\'!\n')

    while True:
        try:
            user_input = input('> ')
        except (KeyboardInterrupt, EOFError):
            print(Fore.LIGHTRED_EX + 'Uh oh... Something unexpected happened. Bye!\n')
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
                print(f'{Fore.LIGHTMAGENTA_EX}{params[1]}\n')
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
                print()
            elif cmd == 7:
                web_services.show_image('random')
                print()
            elif cmd == 8:
                fuzzy.character_threat_calculator()
            elif cmd == 9:
                logic.add_to_kb(params[1].strip())
            elif cmd == 10:
                logic.check_kb(params[1].strip())
            elif cmd == 11:
                print(Fore.LIGHTCYAN_EX + 'Please open the new window to select your image...\n')
                image_classification.image_browser()
            elif cmd == 12:
                azure_services.custom_vision()
            elif cmd == 0:
                similarity.similarity_check(params[1].strip())
        else:
            print(f'{Fore.LIGHTMAGENTA_EX}{answer}\n')
            speak(answer)


if __name__ == '__main__':
    main()

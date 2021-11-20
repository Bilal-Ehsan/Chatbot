import wikipedia
import json
import requests
import aiml
from termcolor import colored
import pyttsx3

api_key = '0e38947d9fd0fa5969c4735f293ab28c'
engine = pyttsx3.init() # Engine instance for the speech synthesis

# The Kernel object is the public interface to the AIML interpreter
kern = aiml.Kernel()
kern.setTextEncoding(None)
kern.bootstrap(learnFiles='bot.xml')

print(colored('\033[1mWelcome to the chatbot! Got a question?\033[0m', 'green'))

# Main loop
while True:
    try:
        user_input = input(colored('> ', 'blue'))
    except (KeyboardInterrupt, EOFError) as e:
        print('\x1B[3mUh oh... Something unexpected happened. Bye!\x1B[0m')
        break
    # Pre-process user input and determine response agent (if needed)
    response_agent = 'aiml'
    # Activate selected response agent
    if response_agent == 'aiml':
        answer = kern.respond(user_input) # Compute response
    # Post-process the answer for commands
    if answer[0] == '#':
        params = answer[1:].split('$')
        cmd = int(params[0])
        if cmd == 0:
            print(colored(params[1], 'magenta'))
            engine.say(params[1])
            engine.runAndWait()
            break
        elif cmd == 1:
            try:
                summary = wikipedia.summary(params[1], sentences=3, auto_suggest=False)
                print(summary)
            except:
                print('\x1B[3mSorry, I do not know that. Be more specific!\x1B[0m')
        elif cmd == 2:
            succeeded = False
            api_url = r'http://api.openweathermap.org/data/2.5/weather?q='
            response = requests.get(api_url + params[1] + (r'&units=metric&APPID='+api_key))
            if response.status_code == 200:
                response_json = json.loads(response.content)
                if response_json:
                    t = response_json['main']['temp']
                    tmi = response_json['main']['temp_min']
                    tma = response_json['main']['temp_max']
                    hum = response_json['main']['humidity']
                    wsp = response_json['wind']['speed']
                    wdir = response_json['wind']['deg']
                    conditions = response_json['weather'][0]['description']
                    print(f'The temperature is {t} °C, varying between {tmi} and {tma} at the' \
                        f' moment, humidity is {hum} %, wind speed {wsp} m/s, {conditions}')
                    succeeded = True
            if not succeeded:
                print('\x1B[3mSorry, I could not resolve the location you gave me.\x1B[0m')
        elif cmd == 99:
            # Similarity-based
            print('\x1B[3mI did not get that, please try again.\x1B[0m')
            print(colored('\x1B[3mReminder: Do similarity-based stuff from here...\x1B[0m', 'red'))
    else:
        print(colored(answer, 'magenta'))
        engine.say(answer)
        engine.runAndWait()

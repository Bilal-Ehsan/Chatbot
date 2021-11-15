import wikipedia
import json
import requests
import aiml

# Insert personal key here if you want to use this
api_key = '5403a1e0442ce1dd18cb1bf7c40e776f'

# The Kernel object is the public interface to the AIML interpreter
kern = aiml.Kernel()
kern.setTextEncoding(None)
kern.bootstrap(learnFiles='bot.xml')

print('Welcome to the chatbot! Got a question?')

# Main loop
while True:
    try:
        user_input = input('> ')
    except (KeyboardInterrupt, EOFError) as e:
        print('Uh oh... Something unexpected happened. Bye!')
        break
    # Pre-process user input and determine response agent (if needed)
    response_agent = 'aiml'
    # Activate selected response agent
    if response_agent == 'aiml':
        answer = kern.respond(user_input) # Compute response
    # Post-process the answer for commands
    if answer[0] == '#':
        params = answer[1:].split('$') # Array of parameters
        cmd = int(params[0])
        if cmd == 0:
            print(params[1])
            break
        elif cmd == 1:
            try:
                summary = wikipedia.summary(params[1], sentences=3, auto_suggest=False)
                print(summary)
            except:
                print('Sorry, I do not know that. Be more specific!')
        elif cmd == 2:
            succeeded = False
            api_url = r'http://api.openweathermap.org/data/2.5/weather?q=' # Raw string
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
                print('Sorry, I could not resolve the location you gave me.')
        elif cmd == 99:
            print('I did not get that, please try again.')
    else:
        print(answer)

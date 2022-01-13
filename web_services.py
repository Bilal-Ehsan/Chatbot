import json
import os
import requests
import random
import webbrowser

import wikipedia

from colorama import Fore


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
            print(f'\n{Fore.LIGHTCYAN_EX}{superhero} related info:\n')

            for x, y in power_stats.items():
                print(f'{x.capitalize()} - {y}')
            print()
            for x, y in biography.items():
                print(f'{x.capitalize()} - {y}')
            print()
            for x, y in work.items():
                print(f'{x.capitalize()} - {y}')
            print()
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

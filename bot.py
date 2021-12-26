import wikipedia
import json
import requests
import aiml
import colorama
from colorama import Fore
import pyttsx3
import webbrowser
from dotenv import load_dotenv
import os
import random
import pathlib
import csv
from nltk.tokenize import sent_tokenize, word_tokenize
import gensim
import pandas
from nltk.sem import Expression
from nltk.inference import ResolutionProver


# Initialisations
load_dotenv()
engine = pyttsx3.init()
colorama.init(autoreset=True)
read_expr = Expression.fromstring

# The Kernel object is the public interface to the AIML interpreter
kern = aiml.Kernel()
kern.setTextEncoding(None)
kern.bootstrap(learnFiles='patterns.xml')

kb = []
data = pandas.read_csv(f'{pathlib.Path().resolve()}\csv\knowledge_base.csv', header=None)
[kb.append(read_expr(row)) for row in data[0]]

inputs = [
    read_expr('Superhero(Superman)'),
    read_expr('Supervillain(Thanos)'),
    read_expr('Good(Superman)'),
    read_expr('Bad(Thanos)'),
    read_expr('Extraterrestrial(Thor)'),
    read_expr('Alien(Thor)')
]

# Check initial KB for contradictions
for i in range(len(inputs)):
    result = ResolutionProver().prove(inputs[i], kb)
    if result == False:
        print(Fore.LIGHTRED_EX + '\nInternal contradiction found! Exiting system...')
        quit()

print(Fore.LIGHTGREEN_EX + 'Welcome to the chatbot! I like to talk about superheroes')
print(Fore.LIGHTGREEN_EX + 'For a cool list of prompts, enter "prompts"!')


def show_prompts():
    print(Fore.LIGHTCYAN_EX + '\nTry asking...\n')
    print('Show me the stats of [superhero]')
    print('Show me a picture of [superhero]')
    print('Show me a picture of a random superhero\n')


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


def similarity_check(query):
    try:
        path_to_csv = f'{pathlib.Path().resolve()}\csv\qa_pairs.csv'
        file = open(path_to_csv, newline='')
        reader = csv.reader(file)

        data = []
        for row in reader:
            question = row[0]
            answer = row[1]
            data.append([question, answer])

        tokenised_sentences = []
        for i in range(len(data)):
            tokens = sent_tokenize(data[i][0])
            for line in tokens:
                tokenised_sentences.append(line)

        # Tokenise each word in each sentence
        tokenised_words = [[w.lower() for w in word_tokenize(word)] 
                    for word in tokenised_sentences]
        dictionary = gensim.corpora.Dictionary(tokenised_words)  # Maps every word to a number
        corpus = [dictionary.doc2bow(gen_doc) for gen_doc in tokenised_words]  # Bag of words

        tf_idf = gensim.models.TfidfModel(corpus)

        # Building the index
        sims = gensim.similarities.Similarity('workdir/', tf_idf[corpus],
            num_features=len(dictionary))

        tokenised_query = []
        tokenised_query.append(query)

        for line in tokenised_query:
            query_doc = [w.lower() for w in word_tokenize(line)]
            # Update existing dictionary and create a bag of words
            query_doc_bow = dictionary.doc2bow(query_doc)

        # Perform a similarity query against the corpus
        query_doc_tf_idf = tf_idf[query_doc_bow]

        closest = max(sims[query_doc_tf_idf].tolist())
        closest_line_num = sims[query_doc_tf_idf].tolist().index(closest)
        if closest < 0.7:
            raise Exception('Closest value too low')

        print(Fore.LIGHTMAGENTA_EX + data[closest_line_num][1]) # Answer
        engine.say(data[closest_line_num][1])
        engine.runAndWait()
    except Exception:
        print(Fore.LIGHTRED_EX + 'I did not get that, please try again.')


def add_to_kb(q):
    object, subject = q.split(' is ')
    expr = read_expr(f'{subject.capitalize()}({object.capitalize()})')
    if expr in kb:
        print(Fore.LIGHTMAGENTA_EX + 'I already knew that!')
        return
    result = ResolutionProver().prove(expr, kb)
    if result:
        kb.append(expr)
        print(Fore.LIGHTMAGENTA_EX + 'Okay, I\'ll remember that!')
        engine.say('Okay, I\'ll remember that!')
        engine.runAndWait()
    else:
        print(Fore.LIGHTMAGENTA_EX + 'I don\'t know about that...')
        engine.say('I don\'t know about that....')
        engine.runAndWait()


def check_kb(q):
    object, subject = q.split(' is ')
    expr = read_expr(f'{subject.capitalize()}({object.capitalize()})')  # KB syntax-specific
    result = ResolutionProver().prove(expr, kb)
    if result:
        print(Fore.LIGHTMAGENTA_EX + 'That\'s correct!')
        engine.say('That\'s correct!')
        engine.runAndWait()
    else:
        print(Fore.LIGHTMAGENTA_EX + 'That may not be true...')
        engine.say('That may not be true...')
        engine.runAndWait()


def main():
    while True:
        try:
            user_input = input('> ')
        except (KeyboardInterrupt, EOFError) as e:
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

            if cmd == 0:
                print(Fore.LIGHTMAGENTA_EX + params[1])
                engine.say(params[1])
                engine.runAndWait()
                break
            elif cmd == 1:
                wikipedia_search(params)
            elif cmd == 2:
                get_weather(params)
            elif cmd == 3:
                show_prompts()
            elif cmd == 4:
                show_stats(params[1].strip())
            elif cmd == 5:
                show_image(params[1].strip())
            elif cmd == 6:
                show_image('random')
            elif cmd == 7:
                add_to_kb(params[1].strip())
            elif cmd == 8:
                check_kb(params[1].strip())
            elif cmd == 99:
                similarity_check(params[1].strip())
        else:
            print(Fore.LIGHTMAGENTA_EX + answer)
            engine.say(answer)
            engine.runAndWait()


if __name__ == '__main__':
    main()

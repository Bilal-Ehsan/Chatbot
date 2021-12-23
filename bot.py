import wikipedia
import json
import requests
import aiml
from termcolor import colored
import pyttsx3
import webbrowser
from dotenv import load_dotenv
import os
import random
import pathlib
import csv
from nltk.tokenize import sent_tokenize, word_tokenize
import gensim


load_dotenv()

engine = pyttsx3.init()  # Engine instance for the speech synthesis

# The Kernel object is the public interface to the AIML interpreter
kern = aiml.Kernel()
kern.setTextEncoding(None)
kern.bootstrap(learnFiles='bot.xml')

print(colored('\033[1mWelcome to the chatbot! I like to talk about superheroes!\033[0m', 'green'))
print(colored('\033[1mFor a cool list of prompts, enter \x1B[3mprompts\x1B[0m!\033[0m', 'green'))


def show_prompts():
    print(colored('\nTry asking...\n', 'cyan'))
    print('Show me the stats of \033[1m[superhero]\033[0m')
    print('Show me a picture of \033[1m[superhero]\033[0m')
    print('Show me a picture of a \033[1mrandom\033[0m superhero\n')


def show_stats(superhero):
    try:
        response = requests.get(f'https://superheroapi.com/api/{os.getenv("SUPERHERO_API_KEY")}/search/{superhero}')
        if response.status_code == 200:
            response_json = json.loads(response.content)
            power_stats = response_json['results'][0]['powerstats']
            biography = response_json['results'][0]['appearance']
            work = response_json['results'][0]['work']
            print(colored(f'-> {superhero} related info:\n', 'cyan'))

            for x, y in power_stats.items():
                print(f'{x.capitalize()} - {y}')
            print()
            for x, y in biography.items():
                print(f'{x.capitalize()} - {y}')
            print()
            for x, y in work.items():
                print(f'{x.capitalize()} - {y}')
    except:
        print(f'\x1B[3mSorry, I couldn\'t find the stats of {superhero}!\x1B[0m')


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
        print(f'\x1B[3mSorry, I couldn\'t find a picture of {superhero}!\x1B[0m')


def similarity_check(query):
    path_to_csv = f'{pathlib.Path().resolve()}\qa_pairs.csv'
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
    gen_docs = [[w.lower() for w in word_tokenize(text)] 
                for text in tokenised_sentences]
    dictionary = gensim.corpora.Dictionary(gen_docs)  # Maps every word to a number
    corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]  # Bag of words

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

    print(colored(data[closest_line_num][1], 'magenta'))  # Answer
    engine.say(data[closest_line_num][1])
    engine.runAndWait()
    
    # print('\x1B[3mI did not get that, please try again.\x1B[0m')


def main():
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
            answer = kern.respond(user_input)  # Compute response
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
                    print('\x1B[3mSorry, I could not resolve the location you gave me.\x1B[0m')
            elif cmd == 3:
                show_prompts()
            elif cmd == 4:
                show_stats(params[1].strip())
            elif cmd == 5:
                show_image(params[1].strip())
            elif cmd == 6:
                show_image('random')
            elif cmd == 99:
                similarity_check(params[1].strip())
        else:
            print(colored(answer, 'magenta'))
            engine.say(answer)
            engine.runAndWait()


if __name__ == '__main__':
    main()

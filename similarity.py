import csv
import pathlib

from colorama import Fore
import gensim
from nltk.tokenize import sent_tokenize, word_tokenize

import bot


def similarity_check(query):
    try:
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
        if closest < 0.6:
            raise Exception('Closest value too low')

        print(f'{Fore.LIGHTMAGENTA_EX}{data[closest_line_num][1]}\n')  # Answer
        bot.speak(data[closest_line_num][1])
    except Exception:
        print(Fore.LIGHTRED_EX + 'I did not get that, please try again.\n')

from __future__ import division
import io
import os
import pymorphy2 as pm
import codecs
import string
import operator
import nltk

m = pm.MorphAnalyzer()

for filename in os.listdir('in'):
    words = []
    words2 = ""
    direction = 'out/'
    count = 1
    name = 'chuncked_'
    with io.open(os.path.join('in', filename), 'r', encoding='utf-8') as f:
        text = f.read()
        words = text.split()
        for i in range(len(words)-1):
            if m.parse(words[i])[0].tag.POS == "ADVB" or m.parse(words[i])[0].tag.POS == "VERB" or \
                    m.parse(words[i][:-1])[0].tag.POS == "VERB" or m.parse(words[i])[0].tag.POS == "PRTS" or \
                    m.parse(words[i])[0].tag.POS == "INFN" or m.parse(words[i])[0].tag.POS == "COMP" or \
                    m.parse(words[i])[0].tag.POS == "ADJS" or m.parse(words[i])[0].tag.POS == "GRND" or \
                    m.parse(words[i])[0].tag.POS == "CONJ":
                words2 += " | " + words[i] + " | "
            elif (m.parse(words[i])[0].tag.POS == "NOUN" and m.parse(words[i])[0].tag.case == ("gent" or "accs")):
                words2 += words[i] + " | "
            elif m.parse(words[i])[0].tag.POS == "NOUN" and m.parse(words[i + 1])[0].tag.POS == ("NOUN" or "ADJF") and \
                    m.parse(words[i])[0].tag.case != m.parse(words[i + 1])[0].tag.case and m.parse(words[i + 1])[
                0].tag.case != "gent":
                words2 += words[i] + " | "
            elif (m.parse(words[i])[0].tag.POS == "NOUN" and m.parse(words[i])[0].tag.case != ("nomn" or "accs") and
                  m.parse(words[i + 1])[0].tag.POS == "NOUN" and m.parse(words[i + 1])[0].tag.case == (
                          "nomn" or "accs")):
                words2 += words[i] + " | "
            elif (m.parse(words[i])[0].tag.POS == None and m.parse(words[i][:-1])[0].tag.POS == None and
                  m.parse(words[i][1:])[0].tag.POS == None):
                words2 += " | " + words[i] + " | "
            elif (m.parse(words[i])[0].tag.POS == "NOUN" and m.parse(words[i - 1])[0].tag.POS == "ADJF" or
                  m.parse(words[i - 1])[0].tag.POS == "PRTF") and m.parse(words[i])[0].tag.case == \
                    m.parse(words[i + 1])[0].tag.case:
                words2 += words[i] + " | "
            else:
                words2 += words[i] + " "
        new_file = io.open(direction + name + str(count) + '.txt', 'w', encoding='utf-8')
        new_file.write(words2)
        new_file.close()
        count += 1

punkt = open('stopwords/punkt.txt', 'r', encoding='utf-8').read()
stop = open('stopwords/stop.txt', 'r', encoding='utf-8').read()
pronouns = open('stopwords/pronouns.txt', 'r', encoding='utf-8').read()
preps = open('stopwords/preps.txt', 'r', encoding='utf-8').read()
mystop = open('stopwords/userstop.txt', 'r', encoding='utf-8')

punkt_list = nltk.word_tokenize(punkt)
stop_list = nltk.word_tokenize(stop) + nltk.word_tokenize(pronouns) + nltk.word_tokenize(preps) + nltk.word_tokenize(mystop)

def isPunct(word):
    return len(word) == 1 and (word in string.punctuation or word in punkt_list)

def isNumeric(word):
    try:
        float(word) if '.' in word else int(word)
        return True
    except ValueError:
        return False

def isInitial(word):
    return len(word) == 2 and word[1] == '.'

class RakeKeywordExtractor:

    def __init__(self):
        self.stopwords = set(nltk.corpus.stopwords.words())
        self.top_fraction = 1

    def _generate_candidate_keywords(self, sentences):
        phrase_list = []
        for sentence in sentences:
            words = map(lambda x: '|' if x in self.stopwords or x in stop_list or isNumeric(x) or isInitial(x) else x, \
                        nltk.word_tokenize(sentence.lower()))
            phrase = []
            for word in words:
                if word == '|' or isPunct(word):
                    if len(phrase) > 0:
                        phrase_list.append(phrase)
                        phrase = []
                else:
                    phrase.append(word)
        return phrase_list

    def _calculate_word_scores(self, phrase_list):
        word_freq = nltk.FreqDist()
        word_degree = nltk.FreqDist()
        for phrase in phrase_list:
            degree = len(list(filter(lambda x: not isNumeric(x), phrase))) - 1
            for word in phrase:
                word_freq[word] += 1
                word_degree[word] += degree
        word_scores = {}
        for word in word_freq.keys():
            word_scores[word] = word_degree[word] / word_freq[word]
        return word_scores

    def _calculate_phrase_scores(self, phrase_list, word_scores):
        phrase_scores = {}
        for phrase in phrase_list:
            phrase_score = 0
            for word in phrase:
                phrase_score += word_scores[word]
            phrase_scores[' '.join(phrase)] = phrase_score
        return phrase_scores

    def extract(self, text, incl_scores = False):
        sentences = nltk.sent_tokenize(text)
        phrase_list = self._generate_candidate_keywords(sentences)
        word_scores = self._calculate_word_scores(phrase_list)
        phrase_scores = self._calculate_phrase_scores(phrase_list, word_scores)
        sorted_phrase_scores = sorted(phrase_scores.items(), key = operator.itemgetter(1), reverse = True)
        n_phrases = len(sorted_phrase_scores)
        if incl_scores:
            return sorted_phrase_scores[0 : int(n_phrases / self.top_fraction)]
        else:
            return map(lambda x: x[0], sorted_phrase_scores[0 : int(n_phrases / self.top_fraction)])

rake = RakeKeywordExtractor()

for filename in os.listdir('out'):
    with io.open(os.path.join('out', filename), 'r', encoding='utf-8') as f:
        txt = f.read()

    keywords = rake.extract(txt, incl_scores=True)
    direction = 'keywords/'
    count = 1
    name = 'keywords_from_'
    new_file = io.open(direction + name + str(count) + '.txt', 'w', encoding='utf-8')
    for eachkwrd in keywords:
        new_file.write(str(eachkwrd[0] + ';' + str(eachkwrd[1] + '\n')))
    count += 1
    new_file.close()

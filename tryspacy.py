import io
import spacy
import re

nlp = spacy.load("ru_core_news_sm")

text = ''
f = io.open('text_for_spacy.txt', 'r', encoding='utf-8')
for line in f.readlines():
        print(len(line.split(' ')))
        line = re.sub(r'[0-9]', '', line)
        text += line +'\n'
f.close()

doc = nlp(text)

f = io.open('locatives.txt', 'a', encoding='utf-8')

for ent in doc.ents:
    if ent.label_ == 'LOC':
        f.write(ent.text + '\n')
    print(ent.text, ent.label_)

f.close()
import os
import regex as re
import io

name = 'zhitie_'
count = 1
direction = 'newzhitia/'

for filename in os.listdir('zhitia'):
    with io.open(os.path.join('zhitia', filename), 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_file = io.open(direction + name + str(count) + '.txt', 'a', encoding='utf-8')
    for line in lines:
        text = line.strip()
        if line.isspace():
            continue
        text = re.sub(r'^[?!,.а-яА-ЯёЁa-zA-Z0-9\s]+$', '', text)
        text = re.sub(' ', '', text).strip()
        text = re.sub('\n', '', text).strip()
        text = re.sub(' +', ' ', text)
        new_file.write(text + ' ')
    count +=1
    new_file.close()

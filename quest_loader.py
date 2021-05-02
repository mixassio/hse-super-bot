import os
from os.path import join
import re

def split_filedata(data_for_parse, result=[]):
    if not data_for_parse:
      return result
    question, answer, *tail = data_for_parse
    return split_filedata(tail, [*result, (question, answer)])


def load_questions(dir_path):
    files = os.listdir(dir_path)
    all_questions = []
    for path_file in files:
        with open(join(dir_path, path_file), "r", encoding="koi8_r") as my_file:
            file_contents = my_file.read()
            parse_data = [i.strip() for i in file_contents.split('\n\n') if i.strip().startswith('Вопрос') or i.strip().startswith('Ответ')]
            split_data = split_filedata(parse_data)
            clear = [(re.sub(r'Вопрос \d+:', '', question).replace('\n', ''), re.sub(r'Ответ:', '', answer).replace('\n', '')) for (question, answer) in split_data]
            make_questions = [{'question': question, 'answer': answer} for (question, answer) in clear]
            all_questions = [*all_questions, *make_questions]
    return all_questions
from quotes_processing import QuotesAdapter
from speech_detector import SpeechDetector
from said_comment_tagger import SaidCommentTagger
from verb_tagger import VerbTagger
from character_detector import CharacterDetector
from pipeline import Pipeline
import pandas as pd
import argparse
import os
import re

CR_V_DATA_PATH = "cross_validation_data"
TOKENS = "tokens.txt"
CONCEPTS = "concepts.txt"
WITH_TITLES_CONCEPTS = "concepts_with_titles.txt"
TEST_WITH_TITLES_CONCEPTS = "concepts_with_titles_test.txt"


# --------------------------------------------------------------------
# sys
# --------------------------------------------------------------------

def _get_data_from_cmd():
    parser = argparse.ArgumentParser(description='Train sequence translation for wikification')
    parser.add_argument('-d', type=str, dest='directory', metavar='<directory>',
                        required=False, help='directory for input corpus')
    parser.add_argument('-i', type=str, dest='input_file', metavar='<single input file>',
                        required=False, help='single input file')
    parser.add_argument('-q', type=str, dest='quotes_csvfile', metavar='<quotes csv file>',
                        required=False, help='quotes csv file', default="..\\csv_files\\quotes.csv")
    parser.add_argument('-s', type=str, dest='speech_csvfile', metavar='<speech csv file>',
                        required=False, help='speech csv file', default="..\\csv_files\\speech.csv")
    parser.add_argument('-v', type=str, dest='verb_csvfile', metavar='<verb csv file>',
                        required=False, help='verb csv file', default="..\\csv_files\\verbs.csv")
    parser.add_argument('-o', type=str, dest='output_path', metavar='<output path>',
                        required=False, help='output path', default="..\\output\\")

    args = parser.parse_args()
    directory = args.directory
    input_file = args.input_file
    if directory is None and input_file is None:
        print(parser.exit("Enter either -d directory or -i single file path "))
    quotes_file = args.quotes_csvfile
    speech_file = args.speech_csvfile
    verb_file = args.verb_csvfile
    output_path = args.output_path
    return directory, input_file, quotes_file, speech_file, verb_file, output_path


def _create_folder_if_absent(path):
    if not os.path.exists(path):
        os.makedirs(path)


def _get_list_of_text_files(dirpath):
    file_paths = []
    for dirname, folders, filenames in os.walk(dirpath):
        for name in filenames:
            file_paths.append(os.path.join(dirname, name))
    return file_paths


# --------------------------------------------------------------------
# read and write
# --------------------------------------------------------------------

def _read_csv(path, sep):
    return pd.read_csv(path, index_col=None, sep=sep)


def _read_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()


def _write_to_file(path, dirpath, name, data):
    if dirpath == None:
        output_path = os.path.join(path, os.path.basename(name))
    else:
        if dirpath != path:
            output_path = name.replace(dirpath, os.path.join(path, ''))
        else:
            output_path = os.path
    print("out = ", output_path)
    _create_folder_if_absent(os.path.dirname(output_path))
    with open(output_path, 'w', encoding='utf-8') as file:
        return file.write(data)


def _delete_newlines(text):
    text_ = text.replace("\n         ", "%%%")
    text_ = text_.replace('\n    ', '')
    text_ = text_.replace('     \xa0\xa0     ', '\n')
    text_ = text_.replace("%%%", "\n")
    text_ = re.sub(r'\xa0\xa0', '', text_)
    text_ = re.sub(r'[ ]+', ' ', text_)
    if len(text_.split("\n")) <= 5:
        return text
    else:
        return text_
    
def delete2(text):
    text1 = re.sub(' +', ' ', text)
    text2 = re.sub(r'\n(?P<cap> [а-яё])', r'\g<cap>', text1)
    text3 = re.sub(r'(?P<punc>[^!\?\.\:])\n', r'\g<punc>', text2)
    text4 = re.sub('[  ]+', ' ', text3)
    return text4


def main():
    directory_path, text_path, quotes_path, speech_path, verb_path, output_path = _get_data_from_cmd()

    quotes_rules = _read_csv(quotes_path, ';')
    speech_rules = _read_csv(speech_path, ';')

    quotes_adapter = QuotesAdapter(quotes_rules)
    speech_detector = SpeechDetector(speech_rules)
    said_comment_tagger = SaidCommentTagger()
    verb_tagger = VerbTagger(verb_path)
    character_detector = CharacterDetector()
    pipeline = Pipeline(quotes_adapter, speech_detector, said_comment_tagger, verb_tagger, character_detector)

    if directory_path is None:
        list_of_textfiles = [text_path]
    else:
        list_of_textfiles = _get_list_of_text_files(directory_path)

    for textpath in list_of_textfiles:
        try:
            text = _read_file(textpath)
            text = delete2(text)
            text = pipeline.apply_to(text)
            _write_to_file(output_path, directory_path, textpath, text)
        except UnicodeDecodeError:
            with open("logs.txt", 'a') as logs:
                print("unicode error in", textpath)
                logs.write("unicode error in " + textpath + "\n")


if __name__ == '__main__':
    main()


from quotes_processing import QuotesAdapter
from speech_detector import SpeechDetector
from file_reader import FileReader
from said_comment_tagger import SaidCommentTagger
from verb_tagger import VerbTagger
from character_detector import CharacterDetector
from sentiment_detector import SentimentDetector
from pipeline import Pipeline
import argparse
import os

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
    parser.add_argument('-d', type=str, dest='directory_path', metavar='<directory>',
                        required=False, help='directory for input corpus')
    parser.add_argument('-i', type=str, dest='text_path', metavar='<single input file>',
                        required=False, help='single input file')
    parser.add_argument('-q', type=str, dest='quotes_path', metavar='<quotes csv file>',
                        required=False, help='quotes csv file', default="../csv_files/quotes.csv")
    parser.add_argument('-s', type=str, dest='speech_path', metavar='<speech csv file>',
                        required=False, help='speech csv file', default="../csv_files/speech.csv")
    parser.add_argument('-v', type=str, dest='verb_path', metavar='<verb csv file>',
                        required=False, help='verb csv file', default="../csv_files/verbs.csv")
    parser.add_argument('-o', type=str, dest='output_path', metavar='<output path>',
                        required=False, help='output path', default="../output/")

    args = parser.parse_args()
    directory = args.directory_path
    input_file = args.text_path
    if directory is None and input_file is None:
        print(parser.exit("Enter either -d directory or -i single file path "))
    return args


# --------------------------------------------------------------------
# read and write
# --------------------------------------------------------------------


def _create_folder_if_absent(path):
    if not os.path.exists(path):
        os.makedirs(path)


def _get_list_of_text_files(dirpath):
    file_paths = []
    for dirname, folders, filenames in os.walk(dirpath):
        for name in filenames:
            file_paths.append(os.path.join(dirname, name))
    return file_paths


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


# --------------------------------------------------------------------
# main
# --------------------------------------------------------------------


def main():
    args = _get_data_from_cmd()

    reader = FileReader()
    quotes_adapter = QuotesAdapter(args.quotes_path)
    speech_detector = SpeechDetector(args.speech_path)
    said_comment_tagger = SaidCommentTagger()
    verb_tagger = VerbTagger(args.verb_path)
    sentiment_detectror = SentimentDetector()
    # character_detector = CharacterDetector()
    
    pipeline = Pipeline(reader, quotes_adapter, speech_detector, 
                        said_comment_tagger, verb_tagger, sentiment_detectror)  #, character_detector)

    list_of_textfiles = [args.text_path] if args.directory_path is None else _get_list_of_text_files(args.directory_path)

    for textpath in list_of_textfiles:
        try:
            text = pipeline.apply_to(textpath)
            _write_to_file(args.output_path, args.directory_path, textpath, text)
        except UnicodeDecodeError:
            #TODO: logging
            with open("logs.txt", 'a') as logs:
                print("unicode error in", textpath)
                logs.write("unicode error in " + textpath + "\n")


if __name__ == '__main__':
    main()


import re
from nltk.tokenize import word_tokenize
from .step import PipelineStep
import pymorphy2

morph = pymorphy2.MorphAnalyzer()


class VerbTagger(PipelineStep):
    COMMENT = r'<author_comment>(.+?)</author_comment>'

    def __init__(self, path="csv_files/verbs.csv"):
        super().__init__()
        self.__df_verbs = self.read_dict_csv(path, sep=';')

    def __make_new_comments(self, string):
        for word in word_tokenize(string):
            lemma = morph.parse(word)[0].normal_form
            regex = re.compile(r'((?<=[ \.:<>!-,])|^)' + '(' +
                               re.escape(word) + ')' + r'((?=[ \.:<>!-,]))')
            for line in self.__df_verbs:
                if lemma == line["verb"]:
                    string = re.sub(regex, '<speech_verb ' + 'semantic="' +
                                    str(line['semantic']) + '" emotion="' +
                                    str(line['emotion']) + '">' + word +
                                    '</speech_verb>', string)
        return string

    def __find_comments(self, text):
        comments = re.findall(self.COMMENT, text)
        return comments

    def annotate(self, text):
        comments = self.__find_comments(text)
        dictionary = self.make_dict(comments, self.__make_new_comments)
        for key in dictionary:
            text = re.sub(re.escape(key), dictionary[key], text)
        text = re.sub(r'(?P<verb><speech_verb.+?>)+', r'\g<verb>', text)
        text = re.sub('(</speech_verb>)+', '</speech_verb>', text)
        return text

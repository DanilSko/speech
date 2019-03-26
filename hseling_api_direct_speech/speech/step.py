from abc import abstractmethod
import csv
import os
from bs4 import BeautifulSoup


class PipelineStep:
    def __init__(self):
        pass

    @abstractmethod
    def annotate(self, text):
        pass

    def make_dict(self, list_of_inside_tag_strings, fucntion):
        dictionary = {string: fucntion(string)
                      for string in list_of_inside_tag_strings}
        return dictionary

    def read_csv(self, path, sep):
        template = os.path.join(os.path.abspath(
            os.path.dirname(os.path.dirname(__file__))), path)
        return csv.reader(open(template, "r", encoding="utf-8"), delimiter=sep)

    def read_dict_csv(self, path, sep):
        template = os.path.join(os.path.abspath(
            os.path.dirname(os.path.dirname(__file__))), path)
        reader = csv.DictReader(open(template, "r", encoding='utf-8-sig'),
                                delimiter=sep)
        return list(reader)

    def read_xml(self, text):
        return BeautifulSoup('<text>' + text + '</text>', "lxml")

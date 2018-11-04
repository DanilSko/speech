from abc import abstractmethod
import pandas as pd
from bs4 import BeautifulSoup

class PipelineStep:
    def __init__(self):
        pass

    @abstractmethod
    def annotate(self, text):
        pass

    def make_dict(self, list_of_inside_tag_strings, fucntion):
        dictionary = {string: fucntion(string) for string in list_of_inside_tag_strings}
        return dictionary
    
    def read_csv(self, path, sep):
        return pd.read_csv(path, index_col=None, sep=sep)
    
    def read_xml(self, text):
        return BeautifulSoup('<text>'+text+'</text>', "lxml")

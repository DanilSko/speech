from abc import abstractmethod


class PipelineStep:
    def __init__(self):
        pass

    @abstractmethod
    def annotate(self, text):
        pass

    def make_dict(self, list_of_inside_tag_strings, fucntion):
        dictionary = {string: fucntion(string) for string in list_of_inside_tag_strings}
        return dictionary

from step import PipelineStep
from itertools import zip_longest as zip_long
import texterra
import re
import copy


class CharacterDetector(PipelineStep):
    def __init__(self):
        super().__init__()
        self.t = texterra.API("c41d9b98960e6f6bdfb3452f6b174e5a6554f992")
        self.__t = texterra.API("c41d9b98960e6f6bdfb3452f6b174e5a6554f992")
        self.__coreference_items = None
        self.__said = "said"
        self.__author_comment = "author_comment"
        self.__speech_verb = "speech_verb"
        self.__speech = "speech"

    def __get_speech_from_text(self, text):
        speech_ = re.findall('<{}>(.+?)</{}>'.format(self.__speech, self.__speech), text)
        return speech_

    def __get_said_author_from_text(self, speech):
        said_ = re.findall('<{}>(.+?)</{}>'.format(self.__said, self.__said), speech)
        author_ = re.findall("<{}>(.+?)</{}>".format(self.__author_comment, self.__author_comment), speech)
        return zip_long(said_, author_)

    def __delete_tags(self, text_with_tags):
        return re.sub("<.+?>", '', text_with_tags)

    def __get_coreference_items(self, text):
        coreference_results = next(self.__t.coreference(text, language='ru'))
        for i in coreference_results:
            if i[3] == None and "«" not in i[0]:
                print(i)

    def __get_nerc_items(self, text):
        nerc_results = next(self.__t.named_entities(text, language='ru'))
        list_of_res = []
        for i in nerc_results:
            if i[3] == "PERSON":
                list_of_res.append(i[:3])
        return list_of_res

    def __get_syntactic_items_who(self, text, verb, role):
        syntax_results = next(self.__t.syntax_detection(text))
        for i in zip(syntax_results.tokens, syntax_results.spans, syntax_results.heads, syntax_results.labels):
            if verb != []:
                if verb[0] in list(syntax_results.tokens):
                    verb_index = list(syntax_results.tokens).index(verb[0])
                    if i[-1] == role and i[2] == verb_index:
                        return i[:2]
            elif i[-1] == role:
                return i[:2]
        return None, (0, 0)

    def __add_said_parameters(self, speech_):
        speech_result = copy.deepcopy(speech_)
        said_author_ = self.__get_said_author_from_text(speech_)
        prev_who = None
        for said_, author_ in said_author_:
            who = self.__define_who(author_)
            if who is None and prev_who is not None:
                who = prev_who
            #corresp = self.__define_corresp(self.__delete_tags(speech_), author_, said_)
            if said_ != None:
                said_result = '<said who="{}" corresp="{}" aloud="true" type = "direct">'.format(who, "None")\
                              + said_ + "</said>"
                speech_result = re.sub(re.escape("<{}>".format(self.__said)+said_+"</{}>".format(self.__said)),
                                       said_result,
                                       speech_result)
                prev_who = who
        return speech_result

    def __define_corresp(self, speech, author_, said_, who):
        nerc_corresp = self.__get_nerc_items(said_)
        print(nerc_corresp)
        corresp = next(self.__t.syntax_detection(said_)).to_string
        print(corresp)

    def __define_who(self, author_):
        if author_:
            author_raw = self.__delete_tags(author_)
            speech_verb = re.findall("<{}.*?>(.+?)</{}>".format(self.__speech_verb, self.__speech_verb), author_)

            subject, subject_borders = self.__get_syntactic_items_who(author_raw, speech_verb, role='предик')
            nerc_item_list = self.__get_nerc_items(author_raw)
            if len(nerc_item_list) > 0:
                for ner_start, ner_finish, nerc_item in nerc_item_list:
                    if subject_borders[0] >= ner_start:
                        return nerc_item
            return subject
        else:
            return None

    def __add_tags(self, text, tag):
        return "<{}>".format(tag)+text+"</{}>".format(tag)

    def annotate(self, text):
        speech_ = self.__get_speech_from_text(text)
        dictionary = self.make_dict(speech_, self.__add_said_parameters)
        for key in dictionary:
            text = re.sub(re.escape(key), dictionary[key], text)
        return text

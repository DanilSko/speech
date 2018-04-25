import re
from step import PipelineStep


class SaidCommentTagger(PipelineStep):
    #SEPARATOR = r'»,? [—–-]{1,2} |[.,!?…] [—–-]{1,2} |: \n?«|:[ \n][—–-]{1,2} |», '
    SEPARATOR = r'»,?[ \u00A0][—–-]{1,2}[ \u00A0]|[.,!?…][ \u00A0][—–-]{1,2}[ \u00A0]|:[ \u00A0]\n?«|:[ \u00A0\n][—–-]{1,2}[ \u00A0]|»,[ \u00A0]'
    FIRST_IN_SAID = '-–—−«'
    SPEECH = r'<speech>(.+?)</speech>'
    SAID = "said"
    AUTHOR_COMMENT = "author_comment"

    def __init__(self):
        super().__init__()

    def __said_comment(self, string):
        lst = re.split(self.SEPARATOR, string)
        annotation_result_list = []
        if lst[0]:
            order = self.__define_order(lst[0][0])
            for index, st in enumerate(lst):
                st_with_tag = order[index % 2]['start'] + str(st) + order[index % 2]['end']
                annotation_result_list.append(st_with_tag)
        else:
            pass
        return "".join(annotation_result_list)

    def __define_order(self, first_symbol):
        if first_symbol in self.FIRST_IN_SAID:
            return [{"start": '<{}>'.format(self.SAID), "end": '</{}>'.format(self.SAID)},
                    {"start": '<{}>'.format(self.AUTHOR_COMMENT), "end": '</{}>'.format(self.AUTHOR_COMMENT)}]
        else:
            return [{"start": '<{}>'.format(self.AUTHOR_COMMENT), "end": '</{}>'.format(self.AUTHOR_COMMENT)},
                    {"start": '<{}>'.format(self.SAID), "end": '</{}>'.format(self.SAID)}]

    def __get_speech(self, text):
        lst = re.findall(self.SPEECH, text)
        return lst

    def annotate(self, text):
        speech_list = self.__get_speech(text)
        dictionary = self.make_dict(speech_list, self.__said_comment)
        for key in dictionary:
            text = re.sub(re.escape(key), dictionary[key], text)
        return text

import re
from .step import PipelineStep
from sentimental import Sentimental

sent = Sentimental()


class SaidCommentTagger(PipelineStep):
    SEPARATOR = r'»,?[ \u00A0][—–-]{1,2}[ \u00A0]|[.,!?…]' \
                r'[ \u00A0][—–-]{1,2}[ \u00A0]|:[ \u00A0]\n?«|' \
                r':[ \u00A0\n][—–-]{1,2}[ \u00A0]|»,[ \u00A0]'
    FIRST_IN_SAID = '-–—−«'
    SPEECH = r'<speech>(.+?)</speech>'
    SAID = "said"
    AUTHOR_COMMENT = "author_comment"

    def __init__(self):
        super().__init__()

    def __said_comment(self, string):
        lst = re.split("(" + self.SEPARATOR + ")", string)
        annotation_result_list = []
        if lst[0]:
            order = self.__define_order(lst[0][0])
            for index, st in enumerate(lst):
                tag = order[index % 3]['start']
                if tag == "<said>":
                    tag = tag.replace("<said>",
                                      "<said aloud='True' "
                                      "characteristic='{}' "
                                      "type='direct'>"
                                      .format(
                                          self.__define_sentiment(
                                              str(st))))
                st_with_tag = tag + str(st) + order[index % 3]['end']
                annotation_result_list.append(st_with_tag)
        else:
            pass
        return "".join(annotation_result_list)

    def __define_order(self, first_symbol):
        if first_symbol in self.FIRST_IN_SAID:
            return [{"start": '<{}>'.format(self.SAID),
                     "end": '</{}>'.format(self.SAID)},
                    {"start": '',
                     "end": ''},
                    {"start": '<{}>'.format(self.AUTHOR_COMMENT),
                     "end": '</{}>'.format(self.AUTHOR_COMMENT)}]
        else:
            return [{"start": '<{}>'.format(self.AUTHOR_COMMENT),
                     "end": '</{}>'.format(self.AUTHOR_COMMENT)},
                    {"start": '',
                     "end": ''},
                    {"start": '<{}>'.format(self.SAID),
                     "end": '</{}>'.format(self.SAID)}]

    def __get_speech(self, text):
        lst = re.findall(self.SPEECH, text)
        return lst

    def __define_sentiment(self, said):
        result = sent.analyze(said)
        result = {'negative': result['negative'],
                  'positive': result["positive"]}
        if result['negative'] == result['positive']:
            sentiment = 'neutral'
        else:
            sentiment = sorted(result.items(), key=lambda x: x[1],
                               reverse=True)[0][0]
        return sentiment

    def annotate(self, text):
        speech_list = self.__get_speech(text)
        dictionary = self.make_dict(speech_list, self.__said_comment)
        for key in dictionary:
            text = re.sub(re.escape(key), dictionary[key], text)
        return text

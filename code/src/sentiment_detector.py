from step import PipelineStep
from sentimental import Sentimental
sent = Sentimental()


class SentimentDetector(PipelineStep):
    def __init__(self):
        super().__init__()
        self.__said = "said"
        self.__author_comment = "author_comment"
        self.__speech_verb = "speech_verb"
        self.__speech = "speech"

    def annotate(self, text):
        xml = self.read_xml(text)
        self.__add_attributes(xml)
        return str(xml.find('text'))
    
    def __add_attributes(self, xml):
        saids = xml.findAll('said')
        for said in saids:
            said['aloud'] = 'True'
            said['type'] = 'direct'
            said['characteristic'] = self.__define_characteristic(said)

    def __define_characteristic(self, said):
        result = sent.analyze(said.text)
        result = {'negative': result['negative'],'positive': result["positive"]}
        if result['negative']==result['positive']:
            sentiment='neutral'
        else:
            sentiment = sorted(result.items(),key=lambda x:x[1], reverse=True)[0][0]
        return sentiment
    

import re
from .step import PipelineStep


class QuotesAdapter(PipelineStep):
    QUOTES_OPEN = '«'
    QUOTES_CLOSE = '»'
    SPECIFIC_QUOTES_OPEN = '„“‘„'
    SPECIFIC_QUOTES_CLOSE = '“”’”'

    def __init__(self, path):
        super().__init__()
        self.__rule_df = self.read_csv(path, ';')

    def annotate(self, text):
        text = self.__replace_specific_quotes(text)
        return self.__process(text)

    def __replace_specific_quotes(self, text):
        text = text.replace(self.SPECIFIC_QUOTES_OPEN, self.QUOTES_OPEN)
        text = text.replace(self.SPECIFIC_QUOTES_CLOSE, self.QUOTES_CLOSE)
        return text

    def __process(self, text):
        for ind in self.__rule_df:
            rule = ind[0]
            quote = ind[1]
            text = self.__replace_quotes(rule, quote, text)
        return text

    def __replace_quotes(self, rule, result_quote, text):
        try:
            text = re.sub(rule, result_quote, text)
        except Exception as e:
            print(e)
            print(rule, "=" * 3, "ERROR IN REG EXP")
        return text

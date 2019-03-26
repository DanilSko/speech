from .speech.quotes_processing import QuotesAdapter
from .speech.speech_detector import SpeechDetector
from .speech.file_reader import FileReader
from .speech.verb_tagger import VerbTagger
from .speech.pipeline import Pipeline
from .speech.said_comment_tagger import SaidCommentTagger


def process_data(text):
    reader = FileReader()
    quotes_adapter = QuotesAdapter()
    speech_detector = SpeechDetector()
    said_comment_tagger = SaidCommentTagger()
    verb_tagger = VerbTagger()
    pipeline = Pipeline(reader, quotes_adapter, speech_detector,
                            said_comment_tagger, verb_tagger)
    result = pipeline.apply_to(text)
    return result

import wiktionary_extractor.languages
from wiktionary_extractor.languages import *


def get_extractors(lang):
    lang_mod = getattr(wiktionary_extractor.languages, lang.replace('-', '_'))
    return lang_mod.get_extractors()

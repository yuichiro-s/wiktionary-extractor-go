import os
import json
import warnings

from wiktionary_extractor.extractor import extract_from_path
from wiktionary_extractor.util import get_extractors


class Entry(object):
    def __init__(self, obj):
        lemma, pos, attrs, variants, defs = obj
        self.lemma = lemma
        self.pos = pos
        self.attrs = attrs
        self.variants = variants
        self.defs = defs

    def convert(self):
        return {
            'lemma': self.lemma,
            'pos': self.pos,
            'attrs': self.attrs,
            'variants': [{
                'type': k,
                'form': v
            } for k, v in self.variants],
            'defs': self.defs,
        }

    @classmethod
    def deconvert(cls, obj):
        variants = [(item['type'], item['form']) for item in obj['variants']]
        return Entry(
            [obj['lemma'], obj['pos'], obj['attrs'], variants, obj['defs']])


def assert_entry_equal(correct_entry, parsed_entry):
    def _m(v):
        # make keys comparable
        return map(lambda ts_v: (tuple(ts_v[0]), ts_v[1]), v)

    assert correct_entry.lemma == parsed_entry.lemma
    assert correct_entry.pos == parsed_entry.pos
    assert set(correct_entry.attrs) == set(parsed_entry.attrs)
    assert set(_m(correct_entry.variants)) == set(_m(parsed_entry.variants))
    assert correct_entry.defs == parsed_entry.defs


def assert_equal(correct, parsed):
    assert len(correct) == len(parsed)
    for correct_entry, parsed_entry in zip(sorted(correct), sorted(parsed)):
        assert_entry_equal(correct_entry, parsed_entry)


def get_test_data_dir_path():
    return os.path.join(os.path.dirname(__file__), '..', 'tests', 'data')


def list_test_data(lang):
    datadir = get_test_data_dir_path()
    base_dir_path = os.path.join(datadir, lang)
    html_dir_path = os.path.join(base_dir_path, 'html')
    for root, dirs, files in os.walk(html_dir_path):
        for name in files:
            html_path = os.path.join(root, name)
            yield html_path


def run_extractors_on_test_data(lang):
    extractors = get_extractors(lang)
    for html_path in list_test_data(lang):
        args = html_path, extractors
        parsed = list(map(Entry, extract_from_path(args)))
        yield html_path, parsed


def assert_correct(html_path, parsed):
    json_path = html_path.replace('html', 'json')
    with open(json_path) as json_file:
        correct = json.load(json_file)
        correct_entries = list(map(Entry.deconvert, correct))
        assert_equal(correct_entries, parsed)

class Entry(object):
    def __init__(self, obj):
        lemma, pos, attrs, variants, defs = obj
        self.lemma = lemma
        self.pos = pos
        self.attrs = set(attrs)
        self.variants = set(variants)
        self.defs = defs


def assert_entry_equal(entry):
    dir_path = os.path.join(os.path.dirname(__file__), 'en-es')
    for path in os.listdir(dir_path):
        yield dir_path.join(dir_path, path)
    open()
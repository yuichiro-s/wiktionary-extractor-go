from wiktionary_extractor.common import default_extractor, extract_tables

STEM1 = 'stem1'
STEM2 = 'stem2'
STEM2A = 'stem2a'
STEM3 = 'stem3'

FORMAL_NON_POLITE = 'formal-non-polite'
INFORMAL_NON_POLITE = 'informal-non-polite'
INFORMAL_POLITE = 'informal-polite'
FORMAL_POLITE = 'formal-polite'
TYPES = [
    FORMAL_NON_POLITE,
    INFORMAL_NON_POLITE,
    INFORMAL_POLITE,
    FORMAL_POLITE,
]

PLAIN = 'plain'
INFORMAL = 'informal'
POLITE = 'polite'
FORMAL = 'formal'
ADJ_HONORIFIC_TYPES = [
    PLAIN,
    INFORMAL,
    POLITE,
    FORMAL,
]

INDICATIVE = 'indicative'
INTERROGATIVE = 'interrogative'
HORTATIVE = 'hortative'
IMPERATIVE = 'imperative'
ASSERTIVE = 'assertive'
REASON = 'reason'
CONTRAST = 'contrast'
CONJUNCTION = 'conjunction'
CONDITION = 'condition'
MOTIVE = 'motive'
VERBAL_NOUN = 'verbal-noun'
DETERMINER = 'determiner'

NON_PAST = 'non-past'
PAST = 'past'
PRESENT = 'present'
FUTURE = 'future'

HONORIFIC = 'honorific'


def verb_extractor(node):
    # Note: variants are not parsed here, since 'form-of' class is missing
    obj = default_extractor(node, True)
    if not obj:
        return None
    form, _, _, definitions = obj

    conjugations = []
    conj_types = []
    headline = node.find_next('span', {'class': 'mw-headline'}, text=['Conjugation'])
    if headline is not None:
        prev = headline.find_previous('span', {'class': 'mw-headline'}, text=['Verb', 'Adjective'])
        if prev == node.span:
            # conjugation really belongs to the current entry
            root = headline.find_next('div', {'class': 'NavFrame'})

            p = root.find_previous('p')
            north_korea = p and 'North Korea' in p.text

            if north_korea:
                # 'contains two conjugation tables (north korean and south korean), so use only the latter
                root = root.find_next('div', {'class': 'NavFrame'})

            head_text = root.find('div', {'class': 'NavHead'}).text.strip()
            if head_text.startswith('Selected forms of the adjective'):
                is_adj = True
            elif head_text.startswith('Selected forms of the verb'):
                is_adj = False
            else:
                assert False, ('unknown NavHead', head_text)
            conjugations, conj_types = parse_conjugation_table(root.find('div', {'class': 'NavContent'}), is_adj)

    if 'si-irregular' in conj_types:
        # do not register honorific form as lemma
        return obj

    return form, conj_types, conjugations, definitions


def parse_stems(table):
    trs = table.find_all('tr')
    variants = []
    for tr in trs[1:]:
        th = tr.find('th')
        td = tr.find('td')
        h = th.text.strip()
        content = td.span.text.strip() if td.span else None

        def _f(t, c):
            assert c is not None
            variants.append(([t], c))

        if h == 'Stem 1':
            _f(STEM1, content)
        elif h == 'Stem 2':
            _f(STEM2, content)
        elif h == 'Stem 2a':
            _f(STEM2A, content)
        elif h == 'Stem 3':
            _f(STEM3, content)
        elif h == 'Conjugation type':
            es = td.text.split(',')
            stem = es[0].strip()
            # remove hangul part
            regularity = ''.join(
                map(chr, filter(lambda x: x < 256, map(
                    ord, es[1].strip())))).replace('(', '').replace(')', '')
            if regularity == '/it/eop-irregular':
                regularity = 'it/eop-irregular'

            conj_types = [
                stem,
                regularity,
            ]
        else:
            assert False, ('unknown entry', tr)

    return variants, conj_types


def parse_conjugation_table(root, is_adj):
    tables = root.find_all('table')
    assert 2 <= len(tables) <= 3, tables

    res = []

    # parse stems
    variants, conj_types = parse_stems(tables[0])
    res.extend(variants)

    row_verb_types = [
        [INDICATIVE, NON_PAST],
        [INDICATIVE, PAST],
        [INTERROGATIVE, NON_PAST],
        [INTERROGATIVE, PAST],
        [HORTATIVE],
        [IMPERATIVE],
        [ASSERTIVE],
        None,
        [REASON],
        [CONTRAST],
        [CONJUNCTION],
        [CONDITION],
        [MOTIVE],
        None,
        [VERBAL_NOUN],
        [VERBAL_NOUN, PAST],
        [DETERMINER, PAST],
        [DETERMINER, PRESENT],
        [DETERMINER, FUTURE],
    ]

    row_adj_types = [
        [INDICATIVE, NON_PAST],
        [INDICATIVE, PAST],
        [INTERROGATIVE, NON_PAST],
        [INTERROGATIVE, PAST],
        [ASSERTIVE],
        None,
        [REASON],
        [CONTRAST],
        [CONJUNCTION],
        [CONDITION],
        None,
        [VERBAL_NOUN],
        [VERBAL_NOUN, PAST],
        [DETERMINER, PRESENT],
        [DETERMINER, FUTURE],
    ]

    def _f(table, ts):
        trs = table.find_all('tr')

        def _g(i, types):
            tr = trs[i]
            tds = tr.find_all('td')
            for td, t in zip(tds, TYPES):
                span = td.find('span')
                if span:
                    text = span.text.strip()
                    for form in text.split(','):
                        form = form.strip()
                        res.append((types + [t], form))

        idx = 2
        for row_t in ts:
            tr = trs[idx]
            th = tr.th
            th = th and th.text.strip()
            if th and th == 'Assertive':
                if IMPERATIVE in row_t:
                    # imperative can be skipped
                    continue
            if row_t is not None:
                _g(idx, row_t)
            idx += 1

    def add_honorific(types):
        return map(lambda t: t + [HONORIFIC] if t is not None else None, types)

    if is_adj:
        _f(tables[1], row_adj_types)
        if len(tables) > 2:
            _f(tables[2], add_honorific(row_adj_types))
    else:
        _f(tables[1], row_verb_types)
        if len(tables) > 2:
            # honorific table is almost the same as the non-honorific table except that the latter missing hortative row
            _f(tables[2], add_honorific(filter(lambda t: t != [HORTATIVE], row_verb_types)))

    return res, conj_types


def get_extractors():
    return {
        #'Noun': 'noun',
        #'Hanja': 'hanja',
        'Verb': ('verb', verb_extractor),
        #'Proper noun': 'proper-noun',
        'Adjective': ('adjective', verb_extractor),
        #'Adverb': 'adverb',
        #'Numeral': 'numeral',
        #'Interjection': 'interjection',
        #'Determiner': 'determiner',
        #'Suffix': 'suffix',
        #'Pronoun': 'pronoun',
        #'Particle': 'particle',
        #'Phrase': 'phrase',
        #'Proverb': 'proverb',
        #'Number': 'number',
        #'Prefix': 'prefix',
    }

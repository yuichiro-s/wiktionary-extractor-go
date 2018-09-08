import logging

from wiktionary_extractor.common import default_extractor, get_next, extract_tables, remove_duplicates

# person
PERSON_1_SINGULAR = '1s'
PERSON_2_SINGULAR = '2s'
PERSON_3_SINGULAR = '3s'
PERSON_1_PLURAL = '1p'
PERSON_2_PLURAL = '2p'
PERSON_3_PLURAL = '3p'

# gender/number
MASCULINE = 'm.'
FEMININE = 'f.'
PLURAL = 'pl.'

# tense/mood
INFINITIVE = 'INF'
GERUND = 'GER'
PAST_PARTICIPLE = 'PP'
PRESENT = 'PRES'
IMPERFECT = 'IMPERF'
PRETERITE = 'PRET'
FUTURE = 'FUT'
CONDITIONAL = 'COND'
SUBJUNCTIVE = 'SBJV'
SUBJUNCTIVE_IMPERFECT = 'SBJV-IMPERF'
IMPERATIVE = 'IMP'

# suffixes
SUFFIX_ME = 'me'
SUFFIX_TE = 'te'
SUFFIX_LE = 'le'
SUFFIX_LA = 'la'
SUFFIX_LO = 'lo'
SUFFIX_SE = 'se'
SUFFIX_NOS = 'nos'
SUFFIX_OS = 'os'
SUFFIX_LES = 'les'
SUFFIX_LAS = 'las'
SUFFIX_LOS = 'los'

REFLEXIVE = 'REFL'

# noun
UNCOUNTABLE = 'uncountable'

# adjective
SUPERLATIVE = 'SUP'


def mk_variant_entry(variant_type, variant_form):
    return [variant_type, variant_form]


def filter_variants(variants, supported_variants):
    new_variants = []
    for variant_type, variant_form in variants:
        if variant_type in supported_variants:
            new_variant_type = supported_variants[variant_type]
            new_variants.append(
                mk_variant_entry(new_variant_type, variant_form))
        else:
            logging.warning("Unknown variant type: " + variant_type)
    return new_variants


def noun_extractor(node):
    def extract_attrs(p):
        new_attrs = []
        for i in p.find_all("i"):
            for a in i.find_all('a'):
                if a['title'] and 'Appendix:Glossary' in a['title']:
                    if a.text == UNCOUNTABLE:
                        new_attrs.append(a.text)
        return new_attrs

    form, attrs, variants, definitions = default_extractor(
        node, True, extract_attrs)

    variants = filter_variants(
        variants, {
            "plural": [PLURAL],
            "feminine plural": [FEMININE, PLURAL],
            "feminine": [FEMININE],
            "masculine plural": [MASCULINE, PLURAL],
            "masculine": [MASCULINE],
        })

    return form, attrs, variants, definitions


def adjective_extractor(node):
    form, attrs, variants, definitions = default_extractor(node, True)

    variants = filter_variants(
        variants, {
            "plural": [PLURAL],
            "feminine singular": [FEMININE],
            "feminine plural": [FEMININE, PLURAL],
            "feminine": [FEMININE],
            "masculine plural": [MASCULINE, PLURAL],
            "superlative": [SUPERLATIVE],
        })

    return form, attrs, variants, definitions


def verb_extractor(node):
    form, attrs, variants, definitions = default_extractor(node, True)

    # filterout compound variants of verbs
    definitions = list(filter(lambda d: 'Compound of ' not in d, definitions))

    # parse conjugation table
    conjugations = []
    for head, table in extract_tables(node):
        new_conjugations = []
        is_reflexive = form + 'se' in head or form.endswith('se')
        if 'Conjugation of ' + form in head:
            new_conjugations = parse_conjugation_table(table, is_reflexive)
        elif not is_reflexive and 'Selected combined forms of ' + form in head:
            # don't parse combined form table of a reflexive verb because it's the same as non-reflexive version
            new_conjugations = parse_combined_forms_table(table)
        for conj_type, conj_form in new_conjugations:
            if is_reflexive:
                conj_type = [REFLEXIVE, *conj_type]
            conjugations.append(mk_variant_entry(conj_type, conj_form))

    if conjugations:
        variants = remove_duplicates(new_conjugations)

    return form, attrs, variants, definitions


def get_td(trs, i, j, is_reflexive):
    tds = trs[i].find_all('td')
    res = []
    td = tds[j]
    if is_reflexive:
        res.append(td.text.strip())
    else:
        for span in td.find_all('span'):
            res.append(span.text.strip())
    return res


def parse_conjugation_table(table, is_reflexive):
    res = []
    trs = table.find_all('tr')

    def _g(i, j, *types):
        for item in get_td(trs, i, j, is_reflexive):
            res.append((types, item))

    def _g2(i, t):
        persons = [
            PERSON_1_SINGULAR, PERSON_2_SINGULAR, PERSON_3_SINGULAR,
            PERSON_1_PLURAL, PERSON_2_PLURAL, PERSON_3_PLURAL
        ]
        for j, person in enumerate(persons):
            for item in get_td(trs, i, j, is_reflexive):
                res.append(([t, person], item))

    _g(0, 0, INFINITIVE)
    _g(1, 0, GERUND)
    if not is_reflexive:
        _g(3, 0, PAST_PARTICIPLE, MASCULINE)
        _g(3, 1, PAST_PARTICIPLE, FEMININE)
        _g(4, 0, PAST_PARTICIPLE, MASCULINE, PLURAL)
        _g(4, 1, PAST_PARTICIPLE, FEMININE, PLURAL)

    _g2(8, PRESENT)
    _g2(9, IMPERFECT)
    _g2(10, PRETERITE)
    _g2(11, FUTURE)
    _g2(12, CONDITIONAL)
    _g2(15, SUBJUNCTIVE)
    _g2(16, SUBJUNCTIVE_IMPERFECT)
    _g2(17, SUBJUNCTIVE_IMPERFECT)
    _g2(21, IMPERATIVE)

    return res


def parse_combined_forms_table(table):
    res = []
    trs = table.find_all('tr')

    # sort suffixes by length in a descending order
    suffixes = [
        SUFFIX_ME, SUFFIX_TE, SUFFIX_LE, SUFFIX_LA, SUFFIX_LO, SUFFIX_SE,
        SUFFIX_NOS, SUFFIX_OS, SUFFIX_LES, SUFFIX_LAS, SUFFIX_LOS
    ]
    suffixes.sort(key=lambda s: -len(s))

    def _g(i, t):
        for j in range(6):
            for item in get_td(trs, i, j, False):
                # use longest match
                for suffix in suffixes:
                    if item.endswith(suffix):
                        types = [t, '-' + suffix]
                        res.append((types, item))
                        break

    if len(trs) == 29:
        _g(3, INFINITIVE)
        _g(4, INFINITIVE)
        _g(7, GERUND)
        _g(8, GERUND)
        _g(11, IMPERATIVE)
        _g(12, IMPERATIVE)
        _g(15, IMPERATIVE)
        _g(16, IMPERATIVE)
        _g(19, IMPERATIVE)
        _g(20, IMPERATIVE)
        _g(23, IMPERATIVE)
        _g(24, IMPERATIVE)
        _g(27, IMPERATIVE)
        _g(28, IMPERATIVE)
    else:
        assert len(trs) == 10, 'Unfamiliar number of rows: ' + str(len(trs))

        _g(3, INFINITIVE)
        _g(6, GERUND)
        _g(9, IMPERATIVE)

    return res


def get_extractors():
    return {
        'Noun': ('noun', noun_extractor),
        'Proper noun': ('proper-noun', default_extractor),
        'Adjective': ('adjective', adjective_extractor),
        'Verb': ('verb', verb_extractor),
        'Adverb': ('adverb', default_extractor),
        'Preposition': ('preposition', default_extractor),
        'Conjunction': ('conjunction', default_extractor),
        'Phrase': ('phrase', default_extractor),
        'Numeral': ('numeral', default_extractor),
        'Interjection': ('interjection', default_extractor),
        'Pronoun': ('pronoun', default_extractor),
        'Proverb': ('proverb', default_extractor),
        'Abbreviation': ('abbreviation', default_extractor),
        'Initialism': ('initialism', default_extractor),
        'Determiner': ('determiner', default_extractor),
        'Article': ('article', default_extractor),
    }

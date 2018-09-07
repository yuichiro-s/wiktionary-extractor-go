import logging

from extractors.common import default_extractor, get_next

# mood
INFINITIVE = 'infinitive'
GERUND = 'gerund'
PAST_PARTICIPLE = 'past-participle'
INDICATIVE = 'indicative'
SUBJUNCTIVE = 'subjunctive'
IMPERATIVE = 'imperative'

# number
SINGULAR = 'singular'
PLURAL = 'plural'

# person
PERSON_1 = '1st-person'
PERSON_2 = '2nd-person'
PERSON_3 = '3rd-person'

# gender
MASCULINE = 'masculine'
FEMININE = 'feminine'

# tense
PRESENT = 'present'
IMPERFECT = 'imperfect'
PRETERITE = 'preterite'
FUTURE = 'future'
CONDITIONAL = 'conditional'

# se/ra
RA = 'ra'
SE = 'se'

COMB_INFINITIVE = 'comb-infinitive'
COMB_GERUND = 'comb-gerund'
COMB_IMPERATIVE = 'comb-imperative'

INFORMAL = 'informal'
FORMAL = 'formal'

TO_PERSON_1_PLURAL = 'to-1st-person-plural'
TO_PERSON_2_SINGULAR = 'to-2nd-person-singular'
TO_PERSON_2_PLURAL = 'to-2nd-person-plural'

DATIVE = 'dative'
ACCUSATIVE = 'accusative'

REFLEXIVE = 'reflexive'

# noun
UNCOUNTABLE = 'uncountable'

# adjective
SUPERLATIVE = 'superlative'


def mk_variant_entry(variant_type, variant_form):
    return {'type': variant_type, 'form': variant_form}


def filter_variants(variants, supported_variants):
    new_variants = []
    for variant_type, variant_form in variants:
        if variant_type in supported_variants:
            new_variant_type = mk_name(supported_variants[variant_type])
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
            "feminine singular": [FEMININE, SINGULAR],
            "feminine plural": [FEMININE, PLURAL],
            "feminine": [FEMININE, SINGULAR],
            "masculine plural": [MASCULINE, PLURAL],
            "superlative": [SUPERLATIVE],
        })

    return form, attrs, variants, definitions


def verb_extractor(node):
    form, attrs, variants, definitions = default_extractor(node, True)

    # filterout compound variants of verbs
    definitions = list(filter(lambda d: 'Compound of ' not in d, definitions))

    # parse conjugation table
    div = node
    conjugations = []
    while True:
        div = get_next(div, 'div')
        if div is None:
            break
        if 'NavFrame' in div.get('class'):
            head = div.div.text
            new_conjugations = []
            if 'Conjugation of ' + form in head:
                new_conjugations = parse_conjugation_table(div.table)
            elif 'Selected combined forms of ' + form in head:
                new_conjugations = parse_combined_forms_table(div.table)
            is_reflexive = form + 'se' in head
            for conj_type, conj_form in new_conjugations:
                if is_reflexive:
                    conj_type = mk_name([REFLEXIVE, conj_type])
                conjugations.append(mk_variant_entry(conj_type, conj_form))

    if conjugations:
        variants = conjugations

    return form, attrs, variants, definitions


def get_td(trs, i, j):
    tds = trs[i].find_all('td')
    res = []
    td = tds[j]
    for span in td.find_all('span'):
        res.append(span.text.strip())
    return res


def mk_name(types):
    return '+'.join(types)


def parse_conjugation_table(table):
    res = []
    trs = table.find_all('tr')

    def _g(i, j, *types):
        name = mk_name(types)
        for item in get_td(trs, i, j):
            res.append((name, item))

    _g(0, 0, INFINITIVE)
    _g(1, 0, GERUND)
    _g(3, 0, PAST_PARTICIPLE, SINGULAR, MASCULINE)
    _g(3, 1, PAST_PARTICIPLE, SINGULAR, FEMININE)
    _g(4, 0, PAST_PARTICIPLE, PLURAL, MASCULINE)
    _g(4, 1, PAST_PARTICIPLE, PLURAL, FEMININE)

    _g(8, 0, INDICATIVE, PRESENT, PERSON_1, SINGULAR)
    _g(8, 1, INDICATIVE, PRESENT, PERSON_2, SINGULAR)
    _g(8, 2, INDICATIVE, PRESENT, PERSON_3, SINGULAR)
    _g(8, 3, INDICATIVE, PRESENT, PERSON_1, PLURAL)
    _g(8, 4, INDICATIVE, PRESENT, PERSON_2, PLURAL)
    _g(8, 5, INDICATIVE, PRESENT, PERSON_3, PLURAL)

    _g(9, 0, INDICATIVE, IMPERFECT, PERSON_1, SINGULAR)
    _g(9, 1, INDICATIVE, IMPERFECT, PERSON_2, SINGULAR)
    _g(9, 2, INDICATIVE, IMPERFECT, PERSON_3, SINGULAR)
    _g(9, 3, INDICATIVE, IMPERFECT, PERSON_1, PLURAL)
    _g(9, 4, INDICATIVE, IMPERFECT, PERSON_2, PLURAL)
    _g(9, 5, INDICATIVE, IMPERFECT, PERSON_3, PLURAL)

    _g(10, 0, INDICATIVE, PRETERITE, PERSON_1, SINGULAR)
    _g(10, 1, INDICATIVE, PRETERITE, PERSON_2, SINGULAR)
    _g(10, 2, INDICATIVE, PRETERITE, PERSON_3, SINGULAR)
    _g(10, 3, INDICATIVE, PRETERITE, PERSON_1, PLURAL)
    _g(10, 4, INDICATIVE, PRETERITE, PERSON_2, PLURAL)
    _g(10, 5, INDICATIVE, PRETERITE, PERSON_3, PLURAL)

    _g(11, 0, INDICATIVE, FUTURE, PERSON_1, SINGULAR)
    _g(11, 1, INDICATIVE, FUTURE, PERSON_2, SINGULAR)
    _g(11, 2, INDICATIVE, FUTURE, PERSON_3, SINGULAR)
    _g(11, 3, INDICATIVE, FUTURE, PERSON_1, PLURAL)
    _g(11, 4, INDICATIVE, FUTURE, PERSON_2, PLURAL)
    _g(11, 5, INDICATIVE, FUTURE, PERSON_3, PLURAL)

    _g(12, 0, INDICATIVE, CONDITIONAL, PERSON_1, SINGULAR)
    _g(12, 1, INDICATIVE, CONDITIONAL, PERSON_2, SINGULAR)
    _g(12, 2, INDICATIVE, CONDITIONAL, PERSON_3, SINGULAR)
    _g(12, 3, INDICATIVE, CONDITIONAL, PERSON_1, PLURAL)
    _g(12, 4, INDICATIVE, CONDITIONAL, PERSON_2, PLURAL)
    _g(12, 5, INDICATIVE, CONDITIONAL, PERSON_3, PLURAL)

    _g(15, 0, SUBJUNCTIVE, PRESENT, PERSON_1, SINGULAR)
    _g(15, 1, SUBJUNCTIVE, PRESENT, PERSON_2, SINGULAR)
    _g(15, 2, SUBJUNCTIVE, PRESENT, PERSON_3, SINGULAR)
    _g(15, 3, SUBJUNCTIVE, PRESENT, PERSON_1, PLURAL)
    _g(15, 4, SUBJUNCTIVE, PRESENT, PERSON_2, PLURAL)
    _g(15, 5, SUBJUNCTIVE, PRESENT, PERSON_3, PLURAL)

    _g(16, 0, SUBJUNCTIVE, IMPERFECT, RA, PERSON_1, SINGULAR)
    _g(16, 1, SUBJUNCTIVE, IMPERFECT, RA, PERSON_2, SINGULAR)
    _g(16, 2, SUBJUNCTIVE, IMPERFECT, RA, PERSON_3, SINGULAR)
    _g(16, 3, SUBJUNCTIVE, IMPERFECT, RA, PERSON_1, PLURAL)
    _g(16, 4, SUBJUNCTIVE, IMPERFECT, RA, PERSON_2, PLURAL)
    _g(16, 5, SUBJUNCTIVE, IMPERFECT, RA, PERSON_3, PLURAL)

    _g(17, 0, SUBJUNCTIVE, IMPERFECT, SE, PERSON_1, SINGULAR)
    _g(17, 1, SUBJUNCTIVE, IMPERFECT, SE, PERSON_2, SINGULAR)
    _g(17, 2, SUBJUNCTIVE, IMPERFECT, SE, PERSON_3, SINGULAR)
    _g(17, 3, SUBJUNCTIVE, IMPERFECT, SE, PERSON_1, PLURAL)
    _g(17, 4, SUBJUNCTIVE, IMPERFECT, SE, PERSON_2, PLURAL)
    _g(17, 5, SUBJUNCTIVE, IMPERFECT, SE, PERSON_3, PLURAL)

    _g(21, 1, IMPERATIVE, PRESENT, PERSON_2, SINGULAR)
    _g(21, 2, IMPERATIVE, PRESENT, PERSON_3, SINGULAR)
    _g(21, 3, IMPERATIVE, PRESENT, PERSON_1, PLURAL)
    _g(21, 4, IMPERATIVE, PRESENT, PERSON_2, PLURAL)
    _g(21, 5, IMPERATIVE, PRESENT, PERSON_3, PLURAL)

    return res


def parse_combined_forms_table(table):
    res = []
    trs = table.find_all('tr')

    def _g(i, j, *types):
        name = mk_name(types)
        for item in get_td(trs, i, j):
            res.append((name, item))

    if len(trs) == 29:
        _g(3, 0, COMB_INFINITIVE, DATIVE, PERSON_1, SINGULAR)
        _g(3, 1, COMB_INFINITIVE, DATIVE, PERSON_2, SINGULAR)
        _g(3, 2, COMB_INFINITIVE, DATIVE, PERSON_3, SINGULAR)
        _g(3, 3, COMB_INFINITIVE, DATIVE, PERSON_1, PLURAL)
        _g(3, 4, COMB_INFINITIVE, DATIVE, PERSON_2, PLURAL)
        _g(3, 5, COMB_INFINITIVE, DATIVE, PERSON_3, PLURAL)

        _g(4, 0, COMB_INFINITIVE, ACCUSATIVE, PERSON_1, SINGULAR)
        _g(4, 1, COMB_INFINITIVE, ACCUSATIVE, PERSON_2, SINGULAR)
        _g(4, 2, COMB_INFINITIVE, ACCUSATIVE, PERSON_3, SINGULAR)
        _g(4, 3, COMB_INFINITIVE, ACCUSATIVE, PERSON_1, PLURAL)
        _g(4, 4, COMB_INFINITIVE, ACCUSATIVE, PERSON_2, PLURAL)
        _g(4, 5, COMB_INFINITIVE, ACCUSATIVE, PERSON_3, PLURAL)

        _g(7, 0, COMB_GERUND, DATIVE, PERSON_1, SINGULAR)
        _g(7, 1, COMB_GERUND, DATIVE, PERSON_2, SINGULAR)
        _g(7, 2, COMB_GERUND, DATIVE, PERSON_3, SINGULAR)
        _g(7, 3, COMB_GERUND, DATIVE, PERSON_1, PLURAL)
        _g(7, 4, COMB_GERUND, DATIVE, PERSON_2, PLURAL)
        _g(7, 5, COMB_GERUND, DATIVE, PERSON_3, PLURAL)

        _g(8, 0, COMB_GERUND, ACCUSATIVE, PERSON_1, SINGULAR)
        _g(8, 1, COMB_GERUND, ACCUSATIVE, PERSON_2, SINGULAR)
        _g(8, 2, COMB_GERUND, ACCUSATIVE, PERSON_3, SINGULAR)
        _g(8, 3, COMB_GERUND, ACCUSATIVE, PERSON_1, PLURAL)
        _g(8, 4, COMB_GERUND, ACCUSATIVE, PERSON_2, PLURAL)
        _g(8, 5, COMB_GERUND, ACCUSATIVE, PERSON_3, PLURAL)

        _g(11, 0, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, INFORMAL, DATIVE,
           PERSON_1, SINGULAR)
        _g(11, 1, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, INFORMAL, DATIVE,
           PERSON_2, SINGULAR)
        _g(11, 2, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, INFORMAL, DATIVE,
           PERSON_3, SINGULAR)
        _g(11, 3, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, INFORMAL, DATIVE,
           PERSON_1, PLURAL)
        _g(11, 4, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, INFORMAL, DATIVE,
           PERSON_2, PLURAL)
        _g(11, 5, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, INFORMAL, DATIVE,
           PERSON_3, PLURAL)

        _g(12, 0, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, INFORMAL, ACCUSATIVE,
           PERSON_1, SINGULAR)
        _g(12, 1, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, INFORMAL, ACCUSATIVE,
           PERSON_2, SINGULAR)
        _g(12, 2, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, INFORMAL, ACCUSATIVE,
           PERSON_3, SINGULAR)
        _g(12, 3, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, INFORMAL, ACCUSATIVE,
           PERSON_1, PLURAL)
        _g(12, 4, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, INFORMAL, ACCUSATIVE,
           PERSON_2, PLURAL)
        _g(12, 5, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, INFORMAL, ACCUSATIVE,
           PERSON_3, PLURAL)

        _g(15, 0, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, FORMAL, DATIVE,
           PERSON_1, SINGULAR)
        _g(15, 1, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, FORMAL, DATIVE,
           PERSON_2, SINGULAR)
        _g(15, 2, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, FORMAL, DATIVE,
           PERSON_3, SINGULAR)
        _g(15, 3, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, FORMAL, DATIVE,
           PERSON_1, PLURAL)
        _g(15, 4, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, FORMAL, DATIVE,
           PERSON_2, PLURAL)
        _g(15, 5, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, FORMAL, DATIVE,
           PERSON_3, PLURAL)

        _g(16, 0, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, FORMAL, ACCUSATIVE,
           PERSON_1, SINGULAR)
        _g(16, 1, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, FORMAL, ACCUSATIVE,
           PERSON_2, SINGULAR)
        _g(16, 2, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, FORMAL, ACCUSATIVE,
           PERSON_3, SINGULAR)
        _g(16, 3, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, FORMAL, ACCUSATIVE,
           PERSON_1, PLURAL)
        _g(16, 4, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, FORMAL, ACCUSATIVE,
           PERSON_2, PLURAL)
        _g(16, 5, COMB_IMPERATIVE, TO_PERSON_2_SINGULAR, FORMAL, ACCUSATIVE,
           PERSON_3, PLURAL)

        _g(19, 0, COMB_IMPERATIVE, TO_PERSON_1_PLURAL, DATIVE, PERSON_1,
           SINGULAR)
        _g(19, 1, COMB_IMPERATIVE, TO_PERSON_1_PLURAL, DATIVE, PERSON_2,
           SINGULAR)
        _g(19, 2, COMB_IMPERATIVE, TO_PERSON_1_PLURAL, DATIVE, PERSON_3,
           SINGULAR)
        _g(19, 3, COMB_IMPERATIVE, TO_PERSON_1_PLURAL, DATIVE, PERSON_1,
           PLURAL)
        _g(19, 4, COMB_IMPERATIVE, TO_PERSON_1_PLURAL, DATIVE, PERSON_2,
           PLURAL)
        _g(19, 5, COMB_IMPERATIVE, TO_PERSON_1_PLURAL, DATIVE, PERSON_3,
           PLURAL)

        _g(20, 0, COMB_IMPERATIVE, TO_PERSON_1_PLURAL, ACCUSATIVE, PERSON_1,
           SINGULAR)
        _g(20, 1, COMB_IMPERATIVE, TO_PERSON_1_PLURAL, ACCUSATIVE, PERSON_2,
           SINGULAR)
        _g(20, 2, COMB_IMPERATIVE, TO_PERSON_1_PLURAL, ACCUSATIVE, PERSON_3,
           SINGULAR)
        _g(20, 3, COMB_IMPERATIVE, TO_PERSON_1_PLURAL, ACCUSATIVE, PERSON_1,
           PLURAL)
        _g(20, 4, COMB_IMPERATIVE, TO_PERSON_1_PLURAL, ACCUSATIVE, PERSON_2,
           PLURAL)
        _g(20, 5, COMB_IMPERATIVE, TO_PERSON_1_PLURAL, ACCUSATIVE, PERSON_3,
           PLURAL)

        _g(23, 0, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, INFORMAL, DATIVE,
           PERSON_1, SINGULAR)
        _g(23, 1, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, INFORMAL, DATIVE,
           PERSON_2, SINGULAR)
        _g(23, 2, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, INFORMAL, DATIVE,
           PERSON_3, SINGULAR)
        _g(23, 3, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, INFORMAL, DATIVE,
           PERSON_1, PLURAL)
        _g(23, 4, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, INFORMAL, DATIVE,
           PERSON_2, PLURAL)
        _g(23, 5, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, INFORMAL, DATIVE,
           PERSON_3, PLURAL)

        _g(24, 0, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, INFORMAL, ACCUSATIVE,
           PERSON_1, SINGULAR)
        _g(24, 1, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, INFORMAL, ACCUSATIVE,
           PERSON_2, SINGULAR)
        _g(24, 2, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, INFORMAL, ACCUSATIVE,
           PERSON_3, SINGULAR)
        _g(24, 3, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, INFORMAL, ACCUSATIVE,
           PERSON_1, PLURAL)
        _g(24, 4, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, INFORMAL, ACCUSATIVE,
           PERSON_2, PLURAL)
        _g(24, 5, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, INFORMAL, ACCUSATIVE,
           PERSON_3, PLURAL)

        _g(27, 0, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, FORMAL, DATIVE,
           PERSON_1, SINGULAR)
        _g(27, 1, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, FORMAL, DATIVE,
           PERSON_2, SINGULAR)
        _g(27, 2, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, FORMAL, DATIVE,
           PERSON_3, SINGULAR)
        _g(27, 3, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, FORMAL, DATIVE,
           PERSON_1, PLURAL)
        _g(27, 4, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, FORMAL, DATIVE,
           PERSON_2, PLURAL)
        _g(27, 5, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, FORMAL, DATIVE,
           PERSON_3, PLURAL)

        _g(28, 0, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, FORMAL, ACCUSATIVE,
           PERSON_1, SINGULAR)
        _g(28, 1, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, FORMAL, ACCUSATIVE,
           PERSON_2, SINGULAR)
        _g(28, 2, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, FORMAL, ACCUSATIVE,
           PERSON_3, SINGULAR)
        _g(28, 3, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, FORMAL, ACCUSATIVE,
           PERSON_1, PLURAL)
        _g(28, 4, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, FORMAL, ACCUSATIVE,
           PERSON_2, PLURAL)
        _g(28, 5, COMB_IMPERATIVE, TO_PERSON_2_PLURAL, FORMAL, ACCUSATIVE,
           PERSON_3, PLURAL)

    else:
        assert len(trs) == 10, 'Unfamiliar number of rows: ' + str(len(trs))

        _g(3, 0, COMB_INFINITIVE, ACCUSATIVE, PERSON_1, SINGULAR)
        _g(3, 1, COMB_INFINITIVE, ACCUSATIVE, PERSON_2, SINGULAR)
        _g(3, 2, COMB_INFINITIVE, ACCUSATIVE, PERSON_3, SINGULAR)
        _g(3, 3, COMB_INFINITIVE, ACCUSATIVE, PERSON_1, PLURAL)
        _g(3, 4, COMB_INFINITIVE, ACCUSATIVE, PERSON_2, PLURAL)
        _g(3, 5, COMB_INFINITIVE, ACCUSATIVE, PERSON_3, PLURAL)

        _g(6, 0, COMB_GERUND, ACCUSATIVE, PERSON_1, SINGULAR)
        _g(6, 1, COMB_GERUND, ACCUSATIVE, PERSON_2, SINGULAR)
        _g(6, 2, COMB_GERUND, ACCUSATIVE, PERSON_3, SINGULAR)
        _g(6, 3, COMB_GERUND, ACCUSATIVE, PERSON_1, PLURAL)
        _g(6, 4, COMB_GERUND, ACCUSATIVE, PERSON_2, PLURAL)
        _g(6, 5, COMB_GERUND, ACCUSATIVE, PERSON_3, PLURAL)

        _g(9, 0, COMB_IMPERATIVE, ACCUSATIVE, PERSON_1, SINGULAR)
        _g(9, 1, COMB_IMPERATIVE, ACCUSATIVE, PERSON_2, SINGULAR)
        _g(9, 2, COMB_IMPERATIVE, ACCUSATIVE, PERSON_3, SINGULAR)
        _g(9, 3, COMB_IMPERATIVE, ACCUSATIVE, PERSON_1, PLURAL)
        _g(9, 4, COMB_IMPERATIVE, ACCUSATIVE, PERSON_2, PLURAL)
        _g(9, 5, COMB_IMPERATIVE, ACCUSATIVE, PERSON_3, PLURAL)

    return res


EXTRACTORS = {
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

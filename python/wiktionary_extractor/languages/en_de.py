from wiktionary_extractor.common import default_extractor, get_next, extract_tables, filter_variants, \
    get_th

# noun
GENITIVE = 'GEN'
DIMINUTIVE = 'DIM'
#FEMININE = 'FEM'

# adjective
SUPERLATIVE = 'SUP'
COMPARATIVE = 'COMP'

# verb
INFINITIVE = 'INF'
ZU_INFINITIVE = 'ZU-INF'
PRESENT_PARTICIPLE = 'PRESP'
PAST_PARTICIPLE = 'PP'
PRESENT = 'PRES'
PRETERITE = 'PRET'
IMPERATIVE = 'IMP'
SUBJUNCTIVE_I = 'SBJV-I'
SUBJUNCTIVE_II = 'SBJV-II'
PERSON_1_SINGULAR = '1s'
PERSON_2_SINGULAR = '2s'
PERSON_3_SINGULAR = '3s'
PERSON_1_PLURAL = '1p'
PERSON_2_PLURAL = '2p'
PERSON_3_PLURAL = '3p'


def noun_extractor(node):
    form, attrs, variants, definitions = default_extractor(node, True)

    variants = filter_variants(
        variants,
        {
            "genitive": [],
            "plural": [],
            "diminutive": [DIMINUTIVE],
            #"feminine": [FEMININE],
        })

    for head, table in extract_tables(node):
        if head.startswith('Declension of'):
            variants.extend(get_all_cells([], table, True))

    variants.append(([], form))

    return form, attrs, variants, definitions


def adjective_extractor(node):
    form, attrs, variants, definitions = default_extractor(node, True)

    variants = filter_variants(variants, {
        'superlative': [SUPERLATIVE],
        'comparative': [COMPARATIVE],
    })
    variants.append(([], form))

    for head, table in extract_tables(node):
        if head.startswith('Positive forms of'):
            variants.extend(get_all_cells([], table))
        elif head.startswith('Comparative forms of'):
            variants.extend(get_all_cells([COMPARATIVE], table))
        elif head.startswith('Superlative forms of'):
            variants.extend(get_all_cells([SUPERLATIVE], table))

    return form, attrs, variants, definitions


def get_all_cells(t, table, span=False):
    res = []
    if span:
        a_s = table.find_all('span', {'class': 'Latn'})
    else:
        a_s = table.find_all('a')
    for a in a_s:
        res.append((t, a.text.strip()))
    return res


def verb_extractor(node):
    # Note: variants are not parsed here, since 'form-of' class is missing
    form, attrs, _, definitions = default_extractor(node, True)

    conjugations = []
    if definitions:
        # parse conjugation table
        for head, table in extract_tables(node):
            new_conjugations = []
            if head.lower().startswith('conjugation of'):
                # lower-case match because {{de-conj-auto}} uses lower-cased title
                new_conjugations, auxiliary, separable = parse_conjugation_table(
                    table)
                if separable:
                    form = get_separable_form(new_conjugations)
                attrs.append(auxiliary)
            elif head.startswith('Subordinate-clause forms of'):
                new_conjugations = parse_subordinate_conjugation_table(table)
            conjugations.extend(new_conjugations)

        # add declension of past participle
        presp, pp = get_participles(conjugations)
        conjugations.extend(get_declension_of_participle(pp, PAST_PARTICIPLE))
        conjugations.extend(
            get_declension_of_participle(presp, PRESENT_PARTICIPLE))

    return form, attrs, conjugations, definitions


def get_cell(trs, i, j, direct=False):
    tds = trs[i].find_all('td')
    res = []
    td = tds[j]
    if direct:
        res.append(td.text.strip())
    else:
        # try to find <span> first
        # if not found, use <a>
        tags = td.find_all('span', {'class', 'Latn'})
        if not tags:
            tags = td.find_all('a')
        for tag in tags:
            res.append(tag.text.strip())
    return res


def get_separable_form(conjugations):
    for t, form in conjugations:
        if t == [PRESENT, PERSON_3_PLURAL]:
            verb, prefix = form.split()
            return prefix + '|' + verb
    assert False, 'present 3rd person plural not found'


def get_participles(conjugations):
    pp = None
    presp = None
    for t, form in conjugations:
        if t == [PAST_PARTICIPLE]:
            pp = form
        elif t == [PRESENT_PARTICIPLE]:
            presp = form
    if not pp or not presp:
        assert False, ('participle not found', pp, presp)
    return presp, pp


def get_declension_of_participle(p, t):
    return [([t], p + suffix) for suffix in ['e', 'em', 'en', 'er', 'es']]


def parse_conjugation_table(table):
    res = []
    trs = table.find_all('tr')
    tag = 'a'
    separable = False

    def _g(i, j, types):
        for item in get_cell(trs, i, j):
            res.append((types, item))

    off = 0
    if get_th(trs, 3, 0) == 'zu-infinitive':
        separable = True
        off = 1
        _g(3, 0, [ZU_INFINITIVE])

    def _g2(i, j, types):
        persons = [
            PERSON_1_SINGULAR, PERSON_2_SINGULAR, PERSON_3_SINGULAR,
            PERSON_1_PLURAL, PERSON_2_PLURAL, PERSON_3_PLURAL
        ]
        for di in range(3):
            items_singular = get_cell(trs, i + di, j)
            items_plural = get_cell(trs, i + di, j + 1)
            assert items_singular, (j, trs[i + di])
            assert items_plural, (j, trs[i + di])
            res.append((types + [persons[di]], items_singular[0]))
            res.append((types + [persons[di + 3]], items_plural[0]))

    res.append(([INFINITIVE], get_cell(trs, 0, 0, True)[0]))

    _g(1, 0, [PRESENT_PARTICIPLE])
    _g(2, 0, [PAST_PARTICIPLE])

    auxiliary = get_cell(trs, off + 3, 0)[0]

    _g2(off + 5, 0, [PRESENT])
    _g2(off + 9, 0, [PRETERITE])
    _g2(off + 5, 1, [SUBJUNCTIVE_I])
    _g2(off + 9, 1, [SUBJUNCTIVE_II])

    for item in get_cell(trs, off + 13, 0) + get_cell(trs, off + 13, 1):
        res.append(([IMPERATIVE], item))

    return res, auxiliary, separable


def parse_subordinate_conjugation_table(table):
    res = []
    trs = table.find_all('tr')

    def _g2(i, j, types):
        persons = [
            PERSON_1_SINGULAR, PERSON_2_SINGULAR, PERSON_3_SINGULAR,
            PERSON_1_PLURAL, PERSON_2_PLURAL, PERSON_3_PLURAL
        ]
        for di in range(3):
            items_singular = get_cell(trs, i + di, j)
            items_plural = get_cell(trs, i + di, j + 1)
            res.append((types + [persons[di]], items_singular[0]))
            res.append((types + [persons[di + 3]], items_plural[0]))

    _g2(1, 0, [PRESENT])
    _g2(5, 0, [PRETERITE])
    _g2(1, 1, [SUBJUNCTIVE_I])
    _g2(5, 1, [SUBJUNCTIVE_II])

    return res


def get_extractors():
    return {
        'Noun': ('noun', noun_extractor),
        'Proper noun': ('proper-noun', noun_extractor),
        'Adjective': ('adjective', adjective_extractor),
        #'Participle': ('participle', adjective_extractor),
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
        'Idiom': ('idiom', default_extractor),
        'Ordinal number': ('ordinal-number', default_extractor),
        'Contraction': ('contraction', default_extractor),
    }

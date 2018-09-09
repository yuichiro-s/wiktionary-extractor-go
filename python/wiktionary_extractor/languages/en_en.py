from wiktionary_extractor.common import default_extractor, default_extractor_parse_variants, filter_variants

PERSON_3_SINGULAR = '3s'
PRESENT_PARTICIPLE = 'PRESP'
PAST_PARTICIPLE = 'PP'
SIMPLE_PAST = 'PST'
SIMPLE_PAST_AND_PAST_PARTICIPLE = 'PST&PP'


def verb_extractor(node):
    # Note: variants are not parsed here, since 'form-of' class is missing
    obj = default_extractor(node, True)
    if not obj:
        return None
    form, attrs, variants, definitions = obj

    variants = filter_variants(variants, {
        'third-person singular simple present': [PERSON_3_SINGULAR],
        'present participle': [PRESENT_PARTICIPLE],
        'simple past': [SIMPLE_PAST],
        'past participle': [PAST_PARTICIPLE],
        'simple past and past participle': [SIMPLE_PAST_AND_PAST_PARTICIPLE],
    })

    # decompose SIMPLE_PAST_AND_PAST_PARTICIPLE
    new_variants = []
    for k, v in variants:
        if k == [SIMPLE_PAST_AND_PAST_PARTICIPLE]:
            new_variants.append(([SIMPLE_PAST], v))
            new_variants.append(([PAST_PARTICIPLE], v))
        else:
            new_variants.append((k, v))

    return form, attrs, new_variants, definitions


def get_extractors():
    return {
        'Noun': ('noun', default_extractor_parse_variants),
        'Proper noun': 'proper-noun',
        'Adjective': ('adjective', default_extractor_parse_variants),
        'Verb': ('verb', verb_extractor),
        'Adverb': 'adverb',
        'Interjection': 'interjection',
        'Initialism': 'initialism',
        'Phrase': 'phrase',
        'Prepositional phrase': 'prepositional-phrase',
        'Prefix': 'prefix',
        'Abbreviation': 'abbreviation',
        'Proverb': 'proverb',
        'Suffix': 'suffix',
        'Contraction': 'contraction',
        'Pronoun': 'pronoun',
        'Preposition': 'preposition',
        'Numeral': 'numeral',
        'Conjunction': 'conjunction',
        'Determiner': 'determiner',
        'Number': 'number',
        'Particle': 'particle',
    }

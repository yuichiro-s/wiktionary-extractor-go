import logging


def get_next(tag, name):
    tag = tag.next_sibling
    while tag is not None and getattr(tag, 'name', None) != name:
        tag = tag.next_sibling
    return tag


def extract_tables(node):
    div = node
    while True:
        div = get_next(div, 'div')
        if div is None:
            break
        if 'NavFrame' in div.get('class'):
            head = div.div.text.strip()
            table = div.table
            yield head, table


def default_extractor(node, parse_variants=False, extract_attrs=None):
    # parse form
    p = get_next(node, 'p')
    form = p.strong.text
    assert 'headword' in p.strong['class']

    # parse attributes
    attrs = []
    gender_span = p.span
    if gender_span:
        for abbr in gender_span.find_all('abbr'):
            attrs.append(abbr.text)

    if extract_attrs:
        new_attrs = extract_attrs(p)
        attrs.extend(new_attrs)

    # parse other forms
    variants = []
    if parse_variants:
        last_variant_type = None
        for b in p.find_all("b", {'class': 'form-of'}, recursive=False):
            variant_type = b.previous_sibling.previous_sibling.text

            if variant_type == 'or':
                # expand "or"
                assert last_variant_type is not None
                variant_type = last_variant_type
            else:
                last_variant_type = variant_type

            variant_form = b.text
            variants.append((variant_type, variant_form))

    # parse definitions
    definitions = []
    ol = get_next(p, 'ol')
    for li in ol.find_all('li', recursive=False):
        # remove untranslated definition
        if li.find('a', text='rfdef'):
            continue

        # skip variants
        skip = False
        for span in li.find_all('span', recursive=False):
            if span.has_attr("class") and span['class']:
                if 'form-of-definition' in span['class']:
                    skip = True
                    break
                if 'use-with-mention' in span['class']:
                    skip = True
                    break
        if skip:
            continue

        # remove long description
        for ul in li.find_all('ul'):
            ul.extract()
        for ol in li.find_all('ol'):
            ol.extract()
        for dl in li.find_all('dl'):
            dl.extract()

        definition = li.text.strip()
        assert '\n' not in definition, definition

        # skip unrendered template
        if 'Template:' in definition:
            continue

        if len(definition) > 0:
            definitions.append(definition)

    return form, attrs, variants, definitions


def filter_variants(variants, supported_variants):
    new_variants = []
    for variant_type, variant_form in variants:
        if variant_type in supported_variants:
            new_variant_type = supported_variants[variant_type]
            new_variants.append((new_variant_type, variant_form))
        else:
            assert False, "Unknown variant type: " + variant_type
    return new_variants


def get_th(trs, i, j):
    ths = trs[i].find_all('th')
    th = ths[j]
    return th.text.strip()


def get_cell(trs, i, j, direct=False, tag='span'):
    tds = trs[i].find_all('td')
    res = []
    td = tds[j]
    if direct:
        res.append(td.text.strip())
    else:
        for tag in td.find_all(tag):
            res.append(tag.text.strip())
    return res

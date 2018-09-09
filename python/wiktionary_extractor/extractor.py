import sys
import traceback

from bs4 import BeautifulSoup

from wiktionary_extractor.common import default_extractor


def extract_from_path(args):
    path, extractors = args
    objs = []
    for headline, node in extract_entries(path):
        try:
            new_objs = extract(extractors, headline, node)
            objs.extend(new_objs)
        except Exception as ex:
            print('Error: {}\t{}'.format(path, headline), file=sys.stderr)
            print(ex, file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
    return objs


def extract_entries(path):
    with open(path) as f:
        soup = BeautifulSoup(f, 'lxml')
        clean(soup)
        for child in soup.recursiveChildGenerator():
            name = getattr(child, 'name', None)
            if name is not None:
                if name.startswith('h'):
                    headline = get_headline(child)
                    if headline:
                        yield headline, child


def remove_duplicates(lst):
    res = []
    # filter out duplicates
    hs = set()
    for e in lst:
        h = str(e)
        if h not in hs:
            hs.add(h)
            res.append(e)
    return res


def extract(extractors, headline, node):
    objs = []
    for name, pos_extractor in extractors.items():
        if isinstance(pos_extractor, str):
            pos, extractor = pos_extractor, default_extractor
        else:
            pos, extractor = pos_extractor
        if headline.startswith(name):
            obj = extractor(node)
            if obj:
                form, attrs, variants, definitions = obj
                variants = remove_duplicates(variants)
                obj = [form, pos, attrs, variants, definitions]
                objs.append(obj)
    return objs


def get_headline(node):
    span = node.find('span', {'class', 'mw-headline'})
    if span:
        return span.text
    else:
        return None


def clean(root):
    for e in root.find_all('div', {'class', 'floatright'}):
        e.extract()
    for e in root.find_all('span', {'class', 'maintenance-line'}):
        e.extract()

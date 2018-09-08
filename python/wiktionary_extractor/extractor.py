import sys
import traceback

from bs4 import BeautifulSoup


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


def extract(extractors, headline, node):
    objs = []
    for name, (pos, extractor) in extractors.items():
        if headline.startswith(name):
            form, attrs, variants, definitions = extractor(node)
            if len(definitions) > 0:
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
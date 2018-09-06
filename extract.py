import os
import multiprocessing
import json
import sys

from bs4 import BeautifulSoup

from extractors import en_es, en_de, en_ko, ja_ko

extractors = {}


def main(args):
    global extractors
    if args.lang == 'en-es':
        extractors = en_es.EXTRACTORS
    elif args.lang == 'en-de':
        extractors = en_de.EXTRACTORS
    elif args.lang == 'en-ko':
        extractors = en_ko.EXTRACTORS
    elif args.lang == 'ja-ko':
        extractors = ja_ko.EXTRACTORS
    else:
        raise RuntimeError('Unsupported language: ' + args.lang)

    def get_paths():
        for root in args.root:
            if os.path.isdir(root):
                for name in os.listdir(root):
                    path = os.path.join(root, name)
                    yield path
            else:
                yield root

    if args.worker == 1:
        map_func = map
    else:
        pool = multiprocessing.Pool(args.worker)
        map_func = pool.imap
    for objs in map_func(process, get_paths()):
        for obj in objs:
            print(json.dumps(obj))


def clean(root):
    for e in root.find_all('div', {'class', 'floatright'}):
        e.extract()
    for e in root.find_all('span', {'class', 'maintenance-line'}):
        e.extract()


def extract(headline, node):
    objs = []
    for name, (pos, extractor) in extractors.items():
        if headline.startswith(name):
            form, attrs, variants, definitions = extractor(node)
            if len(definitions) > 0:
                obj = {
                    'pos': pos,
                    'attrs': attrs,
                    'form': form,
                    'variants': variants,
                    'defs': definitions,
                }
                objs.append(obj)
    return objs


def process(path):
    objs = []
    with open(path) as f:
        soup = BeautifulSoup(f, 'lxml')
        clean(soup)
        for child in soup.recursiveChildGenerator():
            name = getattr(child, 'name', None)
            if name is not None:
                if name.startswith('h'):
                    span = child.find('span', {'class', 'mw-headline'})
                    if span:
                        try:
                            objs.extend(extract(span.text, child))
                        except Exception as ex:
                            print(
                                'Error: ' + path,
                                file=sys.stderr)
                            print(ex, file=sys.stderr)
                            import traceback
                            print(traceback.format_exc(), file=sys.stderr)
    return objs


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Extract word definitions')
    parser.add_argument('lang', help='language')
    parser.add_argument('root', nargs='+', help='directory of downloaded HTML')
    parser.add_argument(
        '--worker', type=int, default=1, help='number of workers')

    main(parser.parse_args())

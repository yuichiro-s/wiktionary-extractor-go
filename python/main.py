import json
import multiprocessing
import os
import sys

from wiktionary_extractor.util import get_extractors
from wiktionary_extractor.extractor import extract_from_path


def main(args):
    # get extractors
    extractors = get_extractors(args.lang)

    def generate_paths():
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

    def generate_args(paths):
        for path in paths:
            yield path, extractors

    for objs in map_func(extract_from_path, generate_args(generate_paths())):
        for obj in objs:
            print(json.dumps(obj))
            sys.stdout.flush()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Extract word definitions')
    parser.add_argument('lang', help='language')
    parser.add_argument('root', nargs='+', help='directory of downloaded HTML')
    parser.add_argument(
        '--worker', type=int, default=1, help='number of workers')

    main(parser.parse_args())

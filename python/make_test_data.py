import json
import os

from wiktionary_extractor.test_util import run_extractors_on_test_data


def main(args):
    for html_path, parsed in run_extractors_on_test_data(args.lang):
        json_path = html_path.replace('html', 'json')
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        if not os.path.exists(json_path):
            with open(json_path, 'w') as json_file:
                json.dump(
                    list(map(lambda item: item.convert(), parsed)),
                    json_file,
                    indent=4,
                    sort_keys=True)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Make test data')
    parser.add_argument('lang', help='language')

    main(parser.parse_args())

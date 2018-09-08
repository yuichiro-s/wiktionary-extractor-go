import pytest

from wiktionary_extractor.test_util import assert_correct, run_extractors_on_test_data


@pytest.mark.parametrize('args', run_extractors_on_test_data('en-de'))
def test(args):
    assert_correct(*args)

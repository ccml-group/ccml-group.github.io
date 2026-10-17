"""Offline safety check: synthetic values are never written into the live website."""
import copy
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError
import update_scholar as updater

payload = {
    'search_metadata': {'status': 'Success'},
    'search_parameters': {'author_id': updater.AUTHOR_ID, 'hl': 'en'},
    'cited_by': {'table': [{'citations': {'all': 120}}, {'h_index': {'all': 4}}, {'i10_index': {'all': 3}}],
                 'graph': [{'year': 2024, 'citations': '80'}, {'year': 2025, 'citations': 40}]}
}
with tempfile.TemporaryDirectory() as directory:
    cache = Path(directory) / 'scholar.js'
    updater.save(payload, cache)
    original = cache.read_bytes()
    normalized = json.loads(cache.read_text().split(' = ', 1)[1].removesuffix(';\n'))
    assert normalized['citations'] == 120 and normalized['graph'][0]['citations'] == 80
    bad = []
    for path, value in [
        (('search_parameters','author_id'), 'different-profile'),
        (('search_metadata','status'), 'Error'),
        (('cited_by','table'), []),
        (('cited_by','graph'), []),
        (('cited_by','graph'), [{'year': 2025, 'citations': -1}]),
        (('cited_by','graph'), [{'year': 2025, 'citations': 1}]*2),
        (('cited_by','table'), [{'citations': {'all': True}}, {'h_index': {'all': 4}}, {'i10_index': {'all': 3}}]),
    ]:
        case = copy.deepcopy(payload)
        case[path[0]][path[1]] = value
        bad.append(case)
    bad += [{'error': 'Quota exceeded'}, {}]
    for case in bad:
        try:
            updater.save(case, cache)
        except (ValueError, KeyError, TypeError):
            pass
        else:
            raise AssertionError('Invalid response accepted')
        assert cache.read_bytes() == original, 'Failure damaged cache'
    with patch.dict(updater.os.environ, {'SERPAPI_API_KEY': ''}), patch.object(updater, 'urlopen') as request:
        assert updater.main() == 1
        request.assert_not_called()
    with patch.dict(updater.os.environ, {'SERPAPI_API_KEY': 'test-only'}), patch.object(updater, 'urlopen', side_effect=URLError('test-only')), patch.object(updater, 'save') as save:
        assert updater.main() == 1
        save.assert_not_called()
print('PASS: valid response, profile identity, malformed data, missing key, network failure and cache preservation.')

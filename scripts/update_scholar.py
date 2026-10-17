"""Fetch public Scholar metrics via SerpApi; never replace the cache on failure."""
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
AUTHOR_ID = 'iqaMS78AAAAJ'
CACHE = ROOT / 'data/scholar.js'

def integer(value):
    if isinstance(value, str) and re.fullmatch(r'\d+', value):
        value = int(value)
    if type(value) is not int or value < 0 or value > 1_000_000_000:
        raise ValueError('Invalid nonnegative integer')
    return value

def normalize(payload):
    if payload.get('error') or payload['search_metadata']['status'] != 'Success':
        raise ValueError('Unsuccessful response')
    params = payload['search_parameters']
    if params['author_id'] != AUTHOR_ID or params.get('hl') != 'en':
        raise ValueError('Unexpected profile or language')
    table = {}
    for row in payload['cited_by']['table']:
        for key in ('citations', 'h_index', 'i10_index'):
            if key in row:
                if key in table:
                    raise ValueError('Duplicate metric')
                table[key] = integer(row[key]['all'])
    if len(table) != 3:
        raise ValueError('Incomplete metrics')
    graph = []
    current_year = datetime.now(timezone.utc).year
    for row in payload['cited_by']['graph']:
        year = integer(row['year'])
        if not 1900 <= year <= current_year:
            raise ValueError('Invalid citation year')
        graph.append({'year': year, 'citations': integer(row['citations'])})
    if not graph or len({r['year'] for r in graph}) != len(graph):
        raise ValueError('Missing or duplicate graph years')
    if table['h_index'] ** 2 > table['citations'] or table['i10_index'] * 10 > table['citations']:
        raise ValueError('Inconsistent metrics')
    return {'author_id': AUTHOR_ID, 'updated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            **table, 'graph': sorted(graph, key=lambda r: r['year'])}

def save(payload, path=CACHE):
    data = normalize(payload)  # Validate everything before touching the last good cache.
    content = 'window.CCML_SCHOLAR = ' + json.dumps(data, ensure_ascii=True, indent=2) + ';\n'
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as f:
        temporary = Path(f.name)
        f.write(content)
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)

def main():
    key = os.environ.get('SERPAPI_API_KEY', '').strip()
    if not key:
        print('SERPAPI_API_KEY is missing; existing metrics were kept.', file=sys.stderr)
        return 1
    query = urlencode({'engine': 'google_scholar_author', 'author_id': AUTHOR_ID, 'hl': 'en', 'api_key': key})
    try:
        with urlopen('https://serpapi.com/search.json?' + query, timeout=45) as response:
            payload = json.load(response)
        save(payload)
    except Exception:
        # Provider/HTTP errors may contain the key-bearing URL: do not print them.
        print('Scholar update failed (request or data validation); existing metrics were kept. Check the provider dashboard.', file=sys.stderr)
        return 1
    print('Scholar metrics updated successfully.')
    return 0

if __name__ == '__main__':
    sys.exit(main())

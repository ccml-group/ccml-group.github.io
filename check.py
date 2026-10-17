"""Run with python3 check.py. Checks internal links, anchors and publication data."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re
from html import escape
ROOT = Path(__file__).resolve().parent
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.ids = set(); self.links = []; self.publications = {}; self.h1 = 0
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f"Duplicate ID: {attrs['id']}"
            self.ids.add(attrs['id'])
        if tag == 'h1': self.h1 += 1
        for key in ('href', 'src'):
            if key in attrs: self.links.append(attrs[key])
        if tag == 'img': assert 'alt' in attrs, 'Missing image alt'
        if tag == 'article' and 'data-status' in attrs:
            self.publications[attrs['id']] = (attrs['data-year'], attrs['data-status'])
pages = {p.name: Page(p.read_text()) for p in ROOT.glob('*.html')}
assert len(pages) == 7
for filename, page in pages.items():
    assert page.h1 == 1, filename
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc: continue
        target = unquote(url.path) or filename
        assert (ROOT / target).is_file(), (filename, link)
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids, (filename, link)
pubs = json.loads((ROOT / 'data/publications.json').read_text())
assert len(pubs) == 36
assert len({p['number'] for p in pubs}) == 36
assert sum(p['status'] == 'submitted' for p in pubs) == 4
assert sum(p['status'] == 'accepted' for p in pubs) == 2
assert sum(p['status'] == 'published' for p in pubs) == 30
assert sum(p['status'] == 'preparation' for p in pubs) == 0
assert sum(bool(p['doi']) for p in pubs) == 30
for p in pubs:
    assert pages['publications.html'].publications[f"pub-{p['number']}"] == (str(p['year']), p['status'])
    assert p['title'] and p['authors'] and p['journal']
    article = re.search(r'<article class="publication(?: has-toc)?" id="pub-' + str(p['number']) + r'".*?</article>', (ROOT / 'publications.html').read_text()).group()
    assert all(escape(p[key]) in article for key in ('title', 'authors', 'journal', 'doi'))
print('PASS: 7 pages; local assets, links and anchors; 36 publication records and statuses.')

assert set(pages['index.html'].publications) == {'pub-27', 'pub-20', 'pub-18', 'pub-17'}
news = (ROOT / 'news.html').read_text()
assert news.count('class="news-row"') == 1 and 'Open call' in news
for p in pubs:
    if 'toc' in p:
        assert p['status'] == 'published'
        assert (ROOT / p['toc']['image']).is_file()
        assert escape(p['toc']['alt']) in (ROOT / 'publications.html').read_text()

assert sum('toc' in p for p in pubs) == 30
for p in pubs:
    assert ('toc' in p) == (p['status'] == 'published')
    if 'toc' in p:
        assert p['toc']['image'].startswith('assets/toc/')
page = (ROOT / 'publications.html').read_text()
assert page.count('<figure class="publication-toc">') == 30
assert not re.search(r'<a[^>]*class="publication-toc', page)
for figure in re.findall(r'<figure class="publication-toc">.*?</figure>', page):
    assert '<a ' not in figure

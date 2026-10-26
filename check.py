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
pages = {str(p.relative_to(ROOT)): Page(p.read_text()) for p in [*ROOT.glob('*.html'), *(ROOT / 'ko').glob('*.html')]}
assert len(pages) == 16
for filename, page in pages.items():
    assert page.h1 == 1, filename
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc: continue
        path = ((ROOT / filename).parent / unquote(url.path)).resolve() if url.path else ROOT / filename
        assert path.is_file(), (filename, link)
        target = str(path.relative_to(ROOT))
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids, (filename, link)
pubs = json.loads((ROOT / 'data/publications.json').read_text())
assert len(pubs) == 36
assert len({p['number'] for p in pubs}) == 36
assert sum(p['status'] == 'submitted' for p in pubs) == 3
assert sum(p['status'] == 'accepted' for p in pubs) == 3
assert sum(p['status'] == 'published' for p in pubs) == 30
assert sum(p['status'] == 'preparation' for p in pubs) == 0
assert sum(bool(p['doi']) for p in pubs) == 30
def check_journal(article, pub):
    journal = re.search(r'<p class="journal"[^>]*>(.*?)</p>', article)[1]
    assert re.sub(r'<[^>]+>', '', journal) == escape(pub['journal']), pub['number']
    expected = [escape(pub['journal'].split(', ', 1)[0])] if pub['status'] in {'accepted', 'published'} else []
    assert re.findall(r'<em>(.*?)</em>', journal) == expected, pub['number']

for p in pubs:
    assert pages['publications.html'].publications[f"pub-{p['number']}"] == (str(p['year']), p['status'])
    assert p['title'] and p['authors'] and p['journal']
    article = re.search(r'<article class="publication(?: has-toc)?" id="pub-' + str(p['number']) + r'".*?</article>', (ROOT / 'publications.html').read_text()).group()
    assert all(escape(p[key]) in article for key in ('title', 'doi'))
    check_journal(article, p)
    authors = re.search(r'<p class="authors">(.*?)</p>', article)[1]
    assert re.sub(r'<[^>]+>', '', authors) == escape(p['authors'])
print('PASS: 16 pages; local assets, links and anchors; 36 publication records and statuses.')

assert set(pages['index.html'].publications) == {'pub-27', 'pub-20', 'pub-18', 'pub-17'}
news = (ROOT / 'news.html').read_text()
assert news.count('class="news-row"') == 1 and 'Open call' in news
for p in pubs:
    if 'toc' in p:
        assert p['status'] == 'published'
        assert (ROOT / p['toc']['image']).is_file()
        assert escape(p['toc']['alt']) in (ROOT / 'publications.html').read_text()

assert sum('toc' in p for p in pubs) == 23
fallback_removed = {29, 22, 19, 13, 10, 9, 5}
for p in pubs:
    assert ('toc' in p) == (p['status'] == 'published' and p['number'] not in fallback_removed)
    if 'toc' in p:
        assert p['toc']['image'].startswith('assets/toc/')
        assert p['toc']['kind'] == 'graphical-abstract'
page = (ROOT / 'publications.html').read_text()
assert page.count('<figure class="publication-toc">') == 23
assert not re.search(r'<a[^>]*class="publication-toc', page)
for figure in re.findall(r'<figure class="publication-toc">.*?</figure>', page):
    assert '<a ' not in figure

expected_lead = {2, 3, 7, 11, 15, 17, 18, 20, 21, 22, 23, 26, 27, 28, 29, 31, 32, 33, 34}
for article in re.findall(r'<article class="publication(?: has-toc)?".*?</article>', page):
    number = int(re.search(r'id="pub-(\d+)"', article)[1])
    assert ('class="lead-author"' in article) == (number in expected_lead)

for filename in pages:
    text = (ROOT / filename).read_text()
    ko = filename.startswith('ko/')
    assert f'<html lang="{"ko" if ko else "en"}">' in text
    counterpart = '../' + Path(filename).name if ko else 'ko/' + filename
    assert re.search(r'<a href="' + re.escape(counterpart) + r'"[^>]*data-language-switch', text), filename
    assert 'E243' in text and 'E244' in text and 'B211' in text
    assert ('교수 사무실' if ko else 'PI office') in text
    assert ('연구실' if ko else 'Laboratory') in text
ko_page = (ROOT / 'ko/publications.html').read_text()
assert pages['ko/publications.html'].publications == pages['publications.html'].publications
assert set(pages['ko/index.html'].publications) == set(pages['index.html'].publications)
for pub in pubs:
    article = re.search(r'<article class="publication(?: has-toc)?" id="pub-' + str(pub['number']) + r'".*?</article>', ko_page)[0]
    assert all(escape(pub[key]) in article for key in ('title', 'doi'))
    check_journal(article, pub)
    authors = re.search(r'<p class="authors"[^>]*>(.*?)</p>', article)[1]
    assert re.sub(r'<[^>]+>', '', authors) == escape(pub['authors'])
    assert ('class="lead-author"' in article) == (pub['number'] in expected_lead)
assert ko_page.count('<figure class="publication-toc">') == 23
assert 'Title, author or journal' not in ko_page and 'Underlined' not in ko_page
assert '경험이 없어도' in (ROOT / 'ko/join.html').read_text()
assert '약 6개월의 참여를 권장' in (ROOT / 'ko/join.html').read_text()
assert 'experience is not required' in (ROOT / 'join.html').read_text()
assert 'recommend around six months' in (ROOT / 'join.html').read_text()
print('PASS: reciprocal language links, bilingual addresses and recruitment; publication metadata and authorship preserved.')

rank = {'submitted': 0, 'accepted': 1, 'published': 2, 'preparation': 3}
expected_order = [f"pub-{p['number']}" for p in pubs]
assert [rank[p['status']] for p in pubs] == sorted(rank[p['status']] for p in pubs)
assert expected_order[0] == 'pub-36'
assert next(p for p in pubs if p['number'] == 34)['journal'] == 'Advanced Energy Materials, 2026, Accepted'
for name in ['publications.html', 'ko/publications.html']:
    assert list(pages[name].publications) == expected_order, name
assert '30 published articles, 3 accepted and 3 submitted manuscripts' in page
assert '게재 논문 30건 · 게재 확정 3건 · 투고 중 3건' in ko_page
print('PASS: AEM acceptance, journal details and submitted/accepted/published order in both languages.')

for filename in ['publications.html', 'ko/publications.html']:
    text = (ROOT / filename).read_text()
    assert text.count('* Corresponding author · † Co-first author') == 1
    for article in re.findall(r'<article class="publication(?: has-toc)?".*?</article>', text):
        number = int(re.search(r'id="pub-(\d+)"', article)[1])
        expected = next(p for p in pubs if p['number'] == number).get('toc') is not None
        assert ('has-toc' in article) == expected
        assert ('<figure class="publication-toc">' in article) == expected
print('PASS: 23 graphical abstracts only, no fallback image columns, concise author-symbol legend.')

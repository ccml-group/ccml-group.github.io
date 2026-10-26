"""Run with python3 check.py. Checks internal links, anchors and publication data."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re
from html import escape
from collections import Counter
ROOT = Path(__file__).resolve().parent
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.ids = set(); self.links = []; self.publications = {}; self.h1 = 0; self.metadata = {}; self.images = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f"Duplicate ID: {attrs['id']}"
            self.ids.add(attrs['id'])
        if tag == 'h1': self.h1 += 1
        for key in ('href', 'src'):
            if key in attrs: self.links.append(attrs[key])
        if tag == 'meta': self.metadata[attrs.get('property', attrs.get('name'))] = attrs.get('content')
        if tag == 'img':
            assert 'alt' in attrs, 'Missing image alt'
            self.images.append(attrs)
            for candidate in attrs.get('srcset', '').split(','):
                if candidate.strip(): self.links.append(candidate.strip().split()[0])
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
assert pubs and len({p['number'] for p in pubs}) == len(pubs)
assert all(p['status'] in {'submitted', 'accepted', 'published'} for p in pubs)
assert all(p['doi'] for p in pubs if p['status'] == 'published')
counts = Counter(p['status'] for p in pubs)
toc_count = sum('toc' in p for p in pubs)
selected = json.loads((ROOT / 'data/selected-publications.json').read_text())
assert len(selected) == len(set(selected)) == 4
def check_journal(article, pub):
    journal = re.search(r'<p class="journal"[^>]*>(.*?)</p>', article)[1]
    badges = re.findall(r' <strong class="impact-factor" data-jif-year="(\d+)" title="([^"]+)">\[IF=([\d.]+)\]</strong>', journal)
    metric = pub.get('impact_factor')
    assert len(badges) == (1 if metric else 0), pub['number']
    if metric:
        assert badges[0][0] == str(metric['year']) and badges[0][2] == metric['value'], pub['number']
        assert f"{metric['year']} JIF" in badges[0][1]
        assert re.search(r' <strong class="impact-factor"[^>]*>\[IF=[\d.]+\]</strong>$', journal), pub['number']
    metadata = re.sub(r' <strong class="impact-factor".*?</strong>', '', journal)
    assert re.sub(r'<[^>]+>', '', metadata) == escape(pub['journal']), pub['number']
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
print(f'PASS: 16 pages; local assets, links and anchors; {len(pubs)} publication records and statuses.')

assert set(pages['index.html'].publications) == {f'pub-{n}' for n in selected}
news = (ROOT / 'news.html').read_text()
assert news.count('class="news-row"') == 1 and 'Open call' in news
for p in pubs:
    if 'toc' in p:
        assert p['status'] == 'published'
        assert (ROOT / p['toc']['image']).is_file()
        assert escape(p['toc']['alt']) in (ROOT / 'publications.html').read_text()

assert toc_count == sum('has-toc' in a for a in re.findall(r'<article class="publication(?: has-toc)?".*?</article>', (ROOT / 'publications.html').read_text()))
fallback_removed = {29, 22, 19, 13, 10, 9, 5}
for p in pubs:
    if p['number'] in fallback_removed: assert 'toc' not in p
    if 'toc' in p:
        assert p['toc']['image'].startswith('assets/toc/')
        assert p['toc']['kind'] == 'graphical-abstract'
page = (ROOT / 'publications.html').read_text()
assert page.count('<figure class="publication-toc">') == toc_count
assert not re.search(r'<a[^>]*class="publication-toc', page)
for figure in re.findall(r'<figure class="publication-toc">.*?</figure>', page):
    assert '<a ' not in figure

expected_lead = {p['number'] for p in pubs if p.get('pi_lead_author')}
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
assert ko_page.count('<figure class="publication-toc">') == toc_count
assert 'Title, author or journal' not in ko_page and 'Underlined' not in ko_page
assert '경험이 없어도' in (ROOT / 'ko/join.html').read_text()
assert '약 6개월의 참여를 권장' in (ROOT / 'ko/join.html').read_text()
assert 'experience is not required' in (ROOT / 'join.html').read_text()
assert 'recommend around six months' in (ROOT / 'join.html').read_text()
print('PASS: reciprocal language links, bilingual addresses and recruitment; publication metadata and authorship preserved.')

rank = {'submitted': 0, 'accepted': 1, 'published': 2}
expected_order = [f"pub-{p['number']}" for p in sorted(pubs, key=lambda p: (-p['year'], rank[p['status']], -p['number']))]
for name in ['publications.html', 'ko/publications.html']:
    assert list(pages[name].publications) == expected_order, name
assert f"{counts['published']} published articles, {counts['accepted']} accepted and {counts['submitted']} submitted manuscripts" in page
assert f"게재 논문 {counts['published']}건 · 게재 확정 {counts['accepted']}건 · 투고 중 {counts['submitted']}건" in ko_page
print('PASS: journal details and submitted/accepted/published order in both languages.')

for filename in ['publications.html', 'ko/publications.html']:
    text = (ROOT / filename).read_text()
    assert text.count('* Corresponding author · † Co-first author') == 1
    for article in re.findall(r'<article class="publication(?: has-toc)?".*?</article>', text):
        number = int(re.search(r'id="pub-(\d+)"', article)[1])
        expected = next(p for p in pubs if p['number'] == number).get('toc') is not None
        assert ('has-toc' in article) == expected
        assert ('<figure class="publication-toc">' in article) == expected
print(f'PASS: {toc_count} graphical abstracts only, no fallback image columns, concise author-symbol legend.')

from datetime import date
releases = {2022: '2023-06-28', 2023: '2024-06-20', 2024: '2025-06-18', 2025: '2026-06-17'}
metric_count = sum('impact_factor' in p for p in pubs)
assert metric_count == counts['published'] + counts['accepted']
for pub in pubs:
    metric = pub.get('impact_factor')
    assert bool(metric) == (pub['status'] != 'submitted')
    if not metric: continue
    assert re.fullmatch(r'\d+\.\d{1,3}', metric['value']) and float(metric['value']) > 0
    assert urlsplit(metric['source']).scheme == 'https'
    if pub['status'] == 'accepted':
        assert metric['basis'] == 'latest' and metric['year'] < int(metric['checked_on'][:4])
        assert 'publication_date' not in metric
    else:
        assert metric['basis'] == 'publication-time' and metric['publication_date_source']
        published = metric['publication_date']
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}', published):
            date.fromisoformat(published)
            available = [year for year, released in releases.items() if released <= published]
            if available and metric['year'] <= max(releases): assert metric['year'] == max(available), pub['number']
            if 'revision_released_on' in metric:
                assert metric['revision_released_on'] <= published
for filename in ['index.html', 'ko/index.html']:
    for article in re.findall(r'<article class="publication(?: has-toc)?".*?</article>', (ROOT / filename).read_text()):
        number = int(re.search(r'id="pub-(\d+)"', article)[1])
        pub = next(p for p in pubs if p['number'] == number)
        check_journal(article, pub)
        assert all(escape(pub[key]) in article for key in ('title', 'doi'))
for filename in ['publications.html', 'ko/publications.html']:
    text = (ROOT / filename).read_text()
    assert text.count('class="impact-factor"') == metric_count
    assert text.count('class="caption impact-factor-note"') == 1
print(f'PASS: {metric_count} sourced JIFs; publication-time release boundaries; accepted/latest policy; bilingual and selected-publication consistency.')

year_counts = Counter(p['year'] for p in pubs)
assert next(p for p in pubs if p['number'] == 6)['year'] == 2018
for filename in ['publications.html', 'ko/publications.html']:
    text = (ROOT / filename).read_text()
    groups = re.findall(r'<section class="publication-year" data-publication-year="(\d+)".*?</section>', text)
    assert [int(year) for year in groups] == sorted(year_counts, reverse=True)
    for group in re.findall(r'<section class="publication-year".*?</section>', text):
        year = int(re.search(r'data-publication-year="(\d+)"', group)[1])
        articles = re.findall(r'<article class="publication(?: has-toc)?".*?</article>', group)
        assert len(articles) == year_counts[year]
        assert all(f'data-year="{year}"' in article for article in articles)
        assert f'<span class="publication-year-count">({len(articles)})</span>' in group
        assert f'aria-labelledby="publications-{year}"' in group
        assert 'class="caption publication-year-summary"' in group
    assert sum(year_counts.values()) == len(pubs)
print('PASS: descending annual sections, accurate counts, stable publication IDs and corrected 2018 metadata.')

for filename in ['publications.html', 'ko/publications.html']:
    text = (ROOT / filename).read_text()
    main = re.search(r'<main\b.*?</main>', text)[0]
    assert main.count('href="https://scholar.google.com/citations?user=iqaMS78AAAAJ&amp;hl=en"') == 1
    panel = re.search(r'<section class="scholar-panel scholar-panel--publications".*?</section></section>', main)[0]
    assert panel.count('data-scholar-chart') == panel.count('data-scholar-values') == 1
    assert 'aria-labelledby="citation-title"' in panel and '<h2 id="citation-title" class="eyebrow">' in panel
    status = re.search(r'<select id="pub-status">.*?</select>', main)[0]
    assert re.findall(r'<option value="([^"]+)"', status) == ['all', 'published', 'accepted', 'submitted']
print('PASS: integrated citation summary/chart with one Google Scholar link per publication page.')

for filename, page in pages.items():
    assert all(page.metadata.get(key) for key in ['og:title', 'og:description', 'og:url', 'og:image', 'og:image:alt'])
    assert page.metadata['og:image'] == 'https://ccml-group.github.io/assets/share-card.png'
    assert page.metadata['twitter:card'] == 'summary_large_image'
    for img in page.images:
        if 'assets/derived/' in img['src']:
            assert int(img['width']) > 0 and int(img['height']) > 0, filename
for filename in ['research.html', 'ko/research.html']:
    text = (ROOT / filename).read_text()
    figures = re.findall(r'<figure class="research-art">.*?</figure>', text)
    assert len(figures) == 4 and all(figure.count('<a ') == 1 for figure in figures)
    assert len(set(re.findall(r'aria-label="([^"]+)"', ''.join(figures)))) == 4
    assert len(re.findall(r'href="publications.html#pub-\d+"', text)) == 8
    linked_numbers = [int(n) for n in re.findall(r'href="publications.html#pub-(\d+)"', text)]
    for number in linked_numbers + selected:
        pub = next(p for p in pubs if p['number'] == number)
        assert float(pub.get('impact_factor', {}).get('value', 0)) >= 9, f'Representative paper {number}: IF must be at least 9'
for filename in ['publications.html', 'ko/publications.html']:
    for figure in re.findall(r'<figure class="publication-toc">.*?</figure>', (ROOT / filename).read_text()):
        assert re.search(r'width="\d+" height="\d+"', figure)
print('PASS: shared previews, responsive image sources/dimensions, unique figure links and eight related-paper links.')

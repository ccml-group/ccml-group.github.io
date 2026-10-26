"""Generate publication fragments from JSON; --check detects unsaved generated HTML."""
import argparse
from collections import Counter
from html import escape, unescape
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def render_pages():
    pubs = json.loads((ROOT / 'data/publications.json').read_text())
    selected = json.loads((ROOT / 'data/selected-publications.json').read_text())
    images = json.loads((ROOT / 'assets/derived/manifest.json').read_text())['images']
    by_number = {p['number']: p for p in pubs}
    assert len(by_number) == len(pubs), 'Duplicate publication number'
    assert len(selected) == len(set(selected)) == 4 and set(selected) <= by_number.keys()
    for pub in pubs:
        assert pub['status'] in {'published', 'accepted', 'submitted'}
        assert isinstance(pub['year'], int) and pub['title'] and pub['authors']
        assert not pub['doi'] or urlsplit(pub['doi']).scheme == 'https'

    def journal(pub):
        value = escape(pub['journal'])
        if pub['status'] != 'submitted':
            name, rest = value.split(', ', 1)
            value = f'<em>{name}</em>, {rest}'
        metric = pub.get('impact_factor')
        if metric:
            basis = 'latest available, checked ' + metric['checked_on'] if metric['basis'] == 'latest' else 'latest available at publication (' + metric['publication_date'] + ')'
            title = escape(f"{metric['year']} JIF · {basis}", quote=True)
            value += f' <strong class="impact-factor" data-jif-year="{metric["year"]}" title="{title}">[IF={escape(metric["value"])}]</strong>'
        return f'<p class="journal" lang="en">{value}</p>'

    def article(pub, ko, compact=False):
        toc = pub.get('toc') if not compact else None
        number = pub['number']
        state = {'published': '게재 완료', 'accepted': '게재 확정', 'submitted': '투고 중'}[pub['status']]
        content = f'<article class="publication{" has-toc" if toc else ""}" id="pub-{number}" data-year="{pub["year"]}" data-status="{pub["status"]}"><span class="pub-number">{number:02d}</span><div>'
        if ko and not compact:
            content += f'<p class="pub-state">{state}</p>'
        title = escape(pub['title'])
        if pub['doi']:
            title = f'<a href="{escape(pub["doi"], quote=True)}">{title} ↗</a>'
        content += journal(pub) + ('<h3 lang="en">' if ko else '<h3>') + title + '</h3>'
        if not compact:
            authors = escape(pub['authors'])
            if pub.get('pi_lead_author'):
                authors, count = re.subn(r'(?<!\w)Y\. Lee[†*]*', r'<strong class="lead-author">\g<0></strong>', authors)
                assert count == 1, number
            content += '<p class="authors"' + (' lang="en"' if ko else '') + f'>{authors}</p>'
        content += '</div>'
        if toc:
            image = images[toc['image']]
            variant = image['variants'][0]
            path = ('../' if ko else '') + variant['path'] + '?v=' + image['source_sha256'][:10]
            caption = escape(unescape(toc.get('caption_ko' if ko else 'caption_en', '논문 대표 그림' if ko else 'Graphical abstract')))
            content += f'<figure class="publication-toc"><img src="{escape(path, quote=True)}" width="{round(image["width"])}" height="{round(image["height"])}" alt="{escape(toc["alt"], quote=True)}" loading="lazy" decoding="async"><figcaption>{caption}</figcaption></figure>'
        return content + '</article>'

    results = {}
    for ko in [False, True]:
        prefix = 'ko/' if ko else ''
        path = ROOT / prefix / 'publications.html'
        text = path.read_text()
        sections = []
        for year in sorted({p['year'] for p in pubs}, reverse=True):
            group = sorted((p for p in pubs if p['year'] == year), key=lambda p: ({'submitted': 0, 'accepted': 1, 'published': 2}[p['status']], -p['number']))
            counts = Counter(p['status'] for p in group)
            labels = {'published': '게재', 'accepted': '게재 확정', 'submitted': '투고 중'} if ko else {'published': 'published', 'accepted': 'accepted', 'submitted': 'submitted'}
            summary = ' · '.join(f'{label} {counts[state]}편' if ko else f'{counts[state]} {label}' for state, label in labels.items() if counts[state]) if counts['accepted'] + counts['submitted'] else ''
            sections.append(f'<section class="publication-year" data-publication-year="{year}" aria-labelledby="publications-{year}"><h2 class="publication-year-heading" id="publications-{year}">{year} <span class="publication-year-count">({len(group)})</span></h2><p class="caption publication-year-summary"' + ('' if summary else ' hidden') + '>' + summary + '</p>' + ''.join(article(p, ko) for p in group) + '</section>')
        start = text.index('<div id="publication-list">') + len('<div id="publication-list">')
        end = text.index('</div><p class="caption author-symbols"', start)
        text = text[:start] + ''.join(sections) + text[end:]
        counts = Counter(p['status'] for p in pubs)
        summary = f'전체 {len(pubs)}건 · 게재 논문 {counts["published"]}건 · 게재 확정 {counts["accepted"]}건 · 투고 중 {counts["submitted"]}건' if ko else f'{len(pubs)} listed works · {counts["published"]} published articles, {counts["accepted"]} accepted and {counts["submitted"]} submitted manuscripts'
        text, count = re.subn(r'(<div class="publication-top"><p class="caption">).*?(</p></div>)', lambda m: m[1] + summary + m[2], text)
        assert count == 1
        text = re.sub(r'(<p id="result-count"[^>]*>).*?(</p>)', lambda m: m[1] + (f'{len(pubs)}건' if ko else f'{len(pubs)} works') + m[2], text)
        years = '<option value="all">' + ('전체 연도' if ko else 'All years') + '</option>' + ''.join(f'<option>{year}</option>' for year in sorted({p['year'] for p in pubs}, reverse=True))
        text = re.sub(r'(<select id="pub-year">).*?(</select>)', lambda m: m[1] + years + m[2], text)
        results[path] = text
        path = ROOT / prefix / 'index.html'
        text = path.read_text()
        fragments = list(re.finditer(r'<article class="publication(?: has-toc)?".*?</article>', text))
        assert len(fragments) == 4
        results[path] = text[:fragments[0].start()] + ''.join(article(by_number[n], ko, compact=True) for n in selected) + text[fragments[-1].end():]
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    stale = []
    for path, text in render_pages().items():
        if args.check:
            if path.read_text() != text:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(text)
    if stale:
        raise SystemExit('Run python3 scripts/render_publications.py: ' + ', '.join(stale))
    print('PASS: publication fragments match JSON.' if args.check else 'Updated bilingual publication lists and four selected publications.')

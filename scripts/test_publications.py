"""Check adding a manuscript updates both languages without editing site files."""
import json
from pathlib import Path
import shutil
import tempfile
import render_publications as renderer

for raw, displayed in [('4.536', '4.5'), ('4.484', '4.5'), ('21.875', '21.9'), ('22.0', '22.0'), ('8.928', '8.9'), ('8.95', '9.0')]:
    assert renderer.format_impact_factor(raw) == displayed

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    original = renderer.ROOT
    for name in ['data/publications.json', 'data/selected-publications.json', 'assets/derived/manifest.json', 'index.html', 'ko/index.html', 'publications.html', 'ko/publications.html']:
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original / name, root / name)
    renderer.ROOT = root
    data = json.loads((root / 'data/publications.json').read_text())
    selected = json.loads((root / 'data/selected-publications.json').read_text())
    summary_pub = next(pub for pub in data if pub['number'] == selected[0])
    summary_pub['summary_en'] = 'Structure <surface> & function.'
    summary_pub['summary_ko'] = '구조 <표면> & 기능.'
    data.append({'number': 38, 'journal': 'Manuscript, 2027, Submitted', 'authors': 'A. Student, Y. Lee*', 'title': 'Test <surface> & interface', 'doi': '', 'year': 2027, 'status': 'submitted', 'pi_lead_author': True})
    (root / 'data/publications.json').write_text(json.dumps(data))
    results = renderer.render_pages()
    for ko in [False, True]:
        home = results[root / ('ko/index.html' if ko else 'index.html')]
        summary = '구조 &lt;표면&gt; &amp; 기능.' if ko else 'Structure &lt;surface&gt; &amp; function.'
        assert f'<p class="publication-summary">{summary}</p>' in home
        assert home.count('class="publication-summary"') == 4
        assert 'class="publication-summary"' not in results[root / ('ko/publications.html' if ko else 'publications.html')]
    for filename in ['publications.html', 'ko/publications.html']:
        text = results[root / filename]
        assert text.index('id="pub-38"') < text.index('id="pub-37"')
        assert '2027 <span class="publication-year-count">(1)</span>' in text
        assert 'Test &lt;surface&gt; &amp; interface' in text
        assert '<strong class="lead-author">Y. Lee*</strong>' in text
        assert ('전체 38건' if filename.startswith('ko/') else '38 listed works') in text
        article = text.split('id="pub-38"', 1)[1].split('</article>', 1)[0]
        assert 'impact-factor' not in article and 'publication-toc' not in article
    data.append(data[-1])
    (root / 'data/publications.json').write_text(json.dumps(data))
    try:
        renderer.render_pages()
    except AssertionError:
        pass
    else:
        raise AssertionError('Duplicate publication numbers must be rejected')
print('PASS: new manuscript, new year, bilingual counts, escaping, authorship and duplicate-number rejection.')

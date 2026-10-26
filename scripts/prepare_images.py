"""Build display-sized lossless WebP copies; keep all original research artwork."""
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / 'assets/derived'
MANIFEST = DERIVED / 'manifest.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_images():
    research = sorted((ROOT / 'assets/research').glob('*.png'))
    publications = json.loads((ROOT / 'data/publications.json').read_text())
    toc = [ROOT / pub['toc']['image'] for pub in publications if 'toc' in pub]
    assert len(research) == 4
    assert len(toc) == len(set(toc)) and all(path.is_file() for path in research + toc)
    return research + toc


def share_card():
    image = Image.new('RGB', (1200, 630), '#202a3a')
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1200, 8), fill='#c8b992')
    # shortcut: card regeneration uses macOS Arial, select an installed font when rebuilding elsewhere.
    fonts = Path('/System/Library/Fonts/Supplemental')
    bold = lambda size: ImageFont.truetype(str(fonts / 'Arial Bold.ttf'), size)
    regular = lambda size: ImageFont.truetype(str(fonts / 'Arial.ttf'), size)
    # The existing mark.svg geometry, scaled without changing its proportions.
    scale, x, y = 1.5, 80, 76
    point = lambda px, py: (x + scale * px, y + scale * py)
    draw.rounded_rectangle((x, y, x + 96, y + 96), radius=22.5, fill='#202a3a')
    for line in [[(15, 22), (32, 12), (49, 22), (49, 42), (32, 52), (15, 42), (15, 22)],
                 [(15, 22), (32, 32), (49, 22)], [(32, 32), (32, 52)]]:
        draw.line([point(*p) for p in line], fill='#c8b992', width=3)
    for px, py, radius in [(32, 12, 4), (15, 22, 4), (49, 22, 4), (32, 32, 5),
                           (15, 42, 4), (49, 42, 4), (32, 52, 4)]:
        cx, cy = point(px, py)
        r = radius * scale
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill='#a0c9be')
    draw.text((202, 88), 'CCML', font=bold(62), fill='#f8f9fa')
    draw.text((83, 242), 'Computational Chemistry', font=bold(64), fill='#f8f9fa')
    draw.text((83, 326), 'and Materials Lab', font=bold(64), fill='#f8f9fa')
    draw.line((84, 455, 1116, 455), fill='#58606c', width=1)
    draw.text((84, 494), 'DONGGUK UNIVERSITY', font=bold(25), fill='#c8b992')
    draw.text((84, 540), 'Chemical and Biochemical Engineering', font=regular(23), fill='#bbc1cd')
    path = ROOT / 'assets/share-card.png'
    image.save(path, optimize=True)
    return {'path': str(path.relative_to(ROOT)), 'width': 1200, 'height': 630}


def build():
    result = {'version': 1, 'images': {}}
    for source in source_images():
        key = str(source.relative_to(ROOT))
        before = digest(source)
        if source.suffix == '.svg':
            viewbox = [float(n) for n in ET.parse(source).getroot().attrib['viewBox'].split()]
            width, height = viewbox[2:]
            variants = [{'path': key, 'width': width, 'height': height}]
        else:
            with Image.open(source) as image:
                width, height = image.size
                variants = []
                sizes = (640, 960) if source.parent.name == 'research' else (480,)
                for limit in sizes:
                    target_width = min(limit, width)
                    size = (target_width, round(height * target_width / width))
                    output = DERIVED / source.parent.name / f'{source.stem}-{limit}.webp'
                    output.parent.mkdir(parents=True, exist_ok=True)
                    resized = image.resize(size, Image.Resampling.LANCZOS)
                    resized.save(output, 'WEBP', lossless=True, method=6)
                    variants.append({'path': str(output.relative_to(ROOT)), 'width': size[0], 'height': size[1]})
        assert digest(source) == before, f'Original changed: {key}'
        result['images'][key] = {'width': width, 'height': height, 'source_sha256': before, 'variants': variants}
    result['share_card'] = share_card()
    MANIFEST.write_text(json.dumps(result, indent=2) + '\n')
    check()


def check():
    manifest = json.loads(MANIFEST.read_text())
    expected = {str(path.relative_to(ROOT)) for path in source_images()}
    assert set(manifest['images']) == expected
    original_bytes = derived_bytes = 0
    for source, record in manifest['images'].items():
        assert digest(ROOT / source) == record['source_sha256'], source
        original_bytes += (ROOT / source).stat().st_size
        for variant in record['variants']:
            path = ROOT / variant['path']
            derived_bytes += path.stat().st_size
            if path.suffix != '.svg':
                with Image.open(path) as image:
                    assert image.size == (variant['width'], variant['height']), path
                    image.verify()
    with Image.open(ROOT / manifest['share_card']['path']) as image:
        assert image.size == (1200, 630)
        image.verify()
    print(f'PASS: {len(manifest["images"])} source images unchanged; variants and 1200x630 share card verified. '
          f'Originals {original_bytes:,} bytes; all variants {derived_bytes:,} bytes.')


if __name__ == '__main__':
    if sys.argv[1:] == ['--check']:
        check()
    elif not sys.argv[1:]:
        build()
    else:
        raise SystemExit('Usage: python3 scripts/prepare_images.py [--check]')

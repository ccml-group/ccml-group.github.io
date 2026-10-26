const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const root = path.join(__dirname, '..');
const code = fs.readFileSync(path.join(root, 'js/main.js'), 'utf8');

function render(lang, withFilters = true) {
  let activeElement = null;
  function node(properties = {}) {
    const listeners = new Map();
    const attributes = new Map();
    const classes = new Set();
    return Object.assign({
      hidden: false, textContent: '', value: '',
      addEventListener(type, handler) {
        if (!listeners.has(type)) listeners.set(type, []);
        listeners.get(type).push(handler);
      },
      dispatch(type, event = {}) { (listeners.get(type) || []).forEach(handler => handler(event)); },
      setAttribute(name, value) { attributes.set(name, String(value)); },
      getAttribute(name) { return attributes.get(name) ?? null; },
      focus() { activeElement = this; },
      classList: {
        toggle(name, enabled) { enabled ? classes.add(name) : classes.delete(name); },
        contains(name) { return classes.has(name); }
      }
    }, properties);
  }
  const menu = node({hidden: true});
  const navigation = node();
  const language = node();
  const filters = node({hidden: true});
  const search = node();
  const year = node({value: 'all'});
  const status = node({value: 'all'});
  const count = node();
  const empty = node({hidden: true});
  const rows = [
    ['gold', '2026', 'published', 'Gold surfaces — A. Author — Journal of Chemistry'],
    ['titanium', '2026', 'accepted', 'Titanium oxide — B. Author — Materials Letters'],
    ['bismuth', '2026', 'submitted', 'Bismuth photoanodes — C. Author — Manuscript'],
    ['water', '2025', 'published', 'Water interfaces — D. Author — Journal of Chemistry']
  ].map(([id, year, status, textContent]) => node({id, dataset: {year, status}, textContent}));
  const sections = ['2026', '2025'].map(year => {
    const yearCount = node();
    const summary = node();
    const children = rows.filter(row => row.dataset.year === year);
    return node({
      yearCount, summary,
      querySelector: selector => ({'.publication-year-count': yearCount, '.publication-year-summary': summary})[selector],
      querySelectorAll: selector => selector === '.publication' ? children : []
    });
  });
  const selectors = {
    '.menu-button': menu, '#navigation': navigation, '.filters': withFilters ? filters : null,
    '#pub-search': search, '#pub-year': year, '#pub-status': status,
    '#result-count': count, '#no-results': empty
  };
  const document = node({
    documentElement: {lang},
    querySelector: selector => selectors[selector],
    querySelectorAll: selector => ({
      '[data-language-switch]': [language], '.publication': rows, '.publication-year': sections
    })[selector] || []
  });
  vm.runInNewContext(code, {document, window: {location: {hash: '#pub-18'}}});
  return {menu, navigation, language, filters, search, year, status, count, empty, rows, sections, document,
    activeElement: () => activeElement,
    visible: () => rows.filter(row => !row.hidden).map(row => row.id)};
}

for (const lang of ['en', 'ko']) {
  const ui = render(lang);
  assert.equal(ui.menu.hidden, false);
  assert.equal(ui.menu.getAttribute('aria-expanded'), 'false');
  assert.equal(ui.navigation.classList.contains('is-collapsed'), true);
  ui.menu.focus();
  ui.menu.dispatch('click');
  assert.equal(ui.menu.getAttribute('aria-expanded'), 'true');
  assert.equal(ui.menu.getAttribute('aria-label'), lang === 'ko' ? '메뉴 닫기' : 'Close navigation');
  assert.equal(ui.navigation.classList.contains('is-collapsed'), false);
  assert.equal(ui.activeElement(), ui.menu);
  ui.navigation.focus();
  ui.document.dispatch('keydown', {key: 'Escape'});
  assert.equal(ui.navigation.classList.contains('is-collapsed'), true);
  assert.equal(ui.menu.getAttribute('aria-expanded'), 'false');
  assert.equal(ui.menu.getAttribute('aria-label'), lang === 'ko' ? '메뉴 열기' : 'Open navigation');
  assert.equal(ui.activeElement(), ui.menu);
  ui.menu.dispatch('click');
  ui.menu.dispatch('click');
  assert.equal(ui.menu.getAttribute('aria-expanded'), 'false');
  ui.language.dispatch('click');
  assert.equal(ui.language.hash, '#pub-18');

  assert.equal(ui.filters.hidden, false);
  ui.year.value = '2026';
  ui.status.value = 'accepted';
  ui.filters.dispatch('change');
  assert.deepEqual(ui.visible(), ['titanium']);
  assert.equal(ui.count.textContent, lang === 'ko' ? '1건' : '1 work');
  assert.equal(ui.sections[0].yearCount.textContent, '(1)');
  assert.equal(ui.sections[0].summary.textContent, lang === 'ko' ? '게재 확정 1편' : '1 accepted');
  assert.equal(ui.sections[0].summary.hidden, false);
  assert.equal(ui.sections[1].hidden, true);

  ui.year.value = '2025';
  ui.filters.dispatch('change');
  assert.deepEqual(ui.visible(), []);
  assert.equal(ui.empty.hidden, false);
  assert.equal(ui.count.textContent, lang === 'ko' ? '0건' : '0 works');
  assert.equal(ui.sections.every(section => section.hidden), true);

  ui.year.value = 'all';
  ui.status.value = 'all';
  ui.search.value = '  JOURNAL OF CHEMISTRY  ';
  ui.filters.dispatch('input');
  assert.deepEqual(ui.visible(), ['gold', 'water']);
  assert.equal(ui.empty.hidden, true);
  assert.equal(ui.sections.every(section => !section.hidden && section.summary.hidden), true);

  ui.search.value = '';
  ui.filters.dispatch('input');
  assert.deepEqual(ui.visible(), ['gold', 'titanium', 'bismuth', 'water']);
  assert.equal(ui.count.textContent, lang === 'ko' ? '4건' : '4 works');
  assert.equal(ui.sections[0].yearCount.textContent, '(3)');
  assert.equal(ui.sections[1].yearCount.textContent, '(1)');
  assert.equal(ui.sections[0].summary.textContent, lang === 'ko'
    ? '게재 1편 · 게재 확정 1편 · 투고 중 1편'
    : '1 published · 1 accepted · 1 submitted');
  let prevented = false;
  ui.filters.dispatch('submit', {preventDefault() { prevented = true; }});
  assert.equal(prevented, true);
  render(lang, false);
}

// Native Tab movement follows HTML order; this VM does not simulate browser focus navigation.
const pages = [root, path.join(root, 'ko')].flatMap(directory => fs.readdirSync(directory)
  .filter(name => name.endsWith('.html')).map(name => path.join(directory, name)));
assert.equal(pages.length, 16);
for (const page of pages) {
  const html = fs.readFileSync(page, 'utf8');
  const button = html.indexOf('<button class="menu-button"');
  const navigation = html.indexOf('<nav id="navigation"');
  assert.ok(button >= 0 && navigation > button, `${path.relative(root, page)}: menu button must precede navigation`);
}
console.log('PASS: English/Korean menu, Escape focus, language anchors, publication filters and 16 header orders.');

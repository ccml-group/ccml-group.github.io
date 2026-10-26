'use strict';
const korean = document.documentElement.lang === 'ko';
document.querySelectorAll('[data-language-switch]').forEach(link => {
  link.addEventListener('click', () => { link.hash = window.location.hash; });
});
const menuButton = document.querySelector('.menu-button');
const navigation = document.querySelector('#navigation');
menuButton.hidden = false;
function setMenu(open) {
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', korean
    ? (open ? '메뉴 닫기' : '메뉴 열기')
    : (open ? 'Close navigation' : 'Open navigation'));
  navigation.classList.toggle('is-collapsed', !open);
}
setMenu(false);
menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
    setMenu(false);
    menuButton.focus();
  }
});
const filters = document.querySelector('.filters');
if (filters) {
  filters.hidden = false;
  const search = document.querySelector('#pub-search');
  const year = document.querySelector('#pub-year');
  const status = document.querySelector('#pub-status');
  const publications = Array.from(document.querySelectorAll('.publication'));
  function filterPublications() {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    publications.forEach(publication => {
      const matches = publication.textContent.toLocaleLowerCase().includes(query)
        && (year.value === 'all' || publication.dataset.year === year.value)
        && (status.value === 'all' || publication.dataset.status === status.value);
      publication.hidden = !matches;
      if (matches) count += 1;
    });
    document.querySelectorAll('.publication-year').forEach(section => {
      const visible = Array.from(section.querySelectorAll('.publication')).filter(publication => !publication.hidden);
      section.hidden = visible.length === 0;
      section.querySelector('.publication-year-count').textContent = `(${visible.length})`;
      const summary = section.querySelector('.publication-year-summary');
      summary.hidden = !visible.some(publication => publication.dataset.status !== 'published');
      const labels = korean
        ? { published: '게재', accepted: '게재 확정', submitted: '투고 중' }
        : { published: 'published', accepted: 'accepted', submitted: 'submitted' };
      summary.textContent = Object.entries(labels).map(([state, label]) => {
        const total = visible.filter(publication => publication.dataset.status === state).length;
        return total ? (korean ? `${label} ${total}편` : `${total} ${label}`) : '';
      }).filter(Boolean).join(' · ');
    });
    document.querySelector('#result-count').textContent = korean ? `${count}건` : `${count} ${count === 1 ? 'work' : 'works'}`;
    document.querySelector('#no-results').hidden = count !== 0;
  }
  filters.addEventListener('submit', event => event.preventDefault());
  filters.addEventListener('input', filterPublications);
  filters.addEventListener('change', filterPublications);
}

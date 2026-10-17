'use strict';
const menuButton = document.querySelector('.menu-button');
const navigation = document.querySelector('#navigation');
menuButton.hidden = false;
function setMenu(open) {
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
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
    document.querySelector('#result-count').textContent = `${count} ${count === 1 ? 'work' : 'works'}`;
    document.querySelector('#no-results').hidden = count !== 0;
  }
  filters.addEventListener('submit', event => event.preventDefault());
  filters.addEventListener('input', filterPublications);
  filters.addEventListener('change', filterPublications);
}

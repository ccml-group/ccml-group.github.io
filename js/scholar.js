'use strict';
const scholar = window.CCML_SCHOLAR;
if (scholar && scholar.author_id === 'iqaMS78AAAAJ'
    && ['citations', 'h_index', 'i10_index'].every(key => Number.isSafeInteger(scholar[key]) && scholar[key] >= 0)
    && !Number.isNaN(Date.parse(scholar.updated_at))) {
  document.querySelectorAll('[data-scholar-metric]').forEach(node => {
    node.textContent = scholar[node.dataset.scholarMetric].toLocaleString('en-US');
  });
  document.querySelectorAll('[data-scholar-date]').forEach(node => {
    const date = new Date(scholar.updated_at);
    node.textContent = `Google Scholar · All-time · Updated ${date.toISOString().slice(0, 10)}`;
    if (Date.now() - date.getTime() > 21 * 86400000) node.textContent += ' · Update delayed';
  });
  document.querySelectorAll('[data-scholar-values]').forEach(node => { node.hidden = false; });
  document.querySelectorAll('[data-scholar-pending]').forEach(node => { node.hidden = true; });
  const graph = document.querySelector('[data-scholar-graph]');
  if (graph && Array.isArray(scholar.graph) && scholar.graph.length
      && scholar.graph.every(row => Number.isInteger(row.year) && Number.isSafeInteger(row.citations) && row.citations >= 0)) {
    const max = Math.max(1, ...scholar.graph.map(row => row.citations));
    scholar.graph.forEach(row => {
      const item = document.createElement('li');
      const year = document.createElement('span');
      year.textContent = row.year;
      const bar = document.createElement('span');
      bar.className = 'citation-bar';
      bar.style.height = `${row.citations / max * 85}%`;
      bar.setAttribute('aria-hidden', 'true');
      const count = document.createElement('strong');
      count.textContent = row.citations.toLocaleString('en-US');
      const track = document.createElement('div');
      track.className = 'citation-track';
      track.append(count, bar);
      item.append(track, year);
      graph.append(item);
    });
    document.querySelector('[data-scholar-chart]').hidden = false;
  }
}

// Synthetic data stays in memory; the delivered site contains no test metrics.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const code = fs.readFileSync(path.join(__dirname, '../js/scholar.js'), 'utf8');
function render(data, lang = 'en') {
  const node = () => ({hidden:true,textContent:'',style:{},children:[],setAttribute(){},append(...items){this.children.push(...items);}});
  const metrics = ['citations','h_index','i10_index'].map(key => Object.assign(node(),{dataset:{scholarMetric:key}}));
  const selectors = Object.fromEntries(['date','values','pending','graph','chart'].map(key => [`[data-scholar-${key}]`,node()]));
  selectors['[data-scholar-pending]'].hidden = false;
  const document = {
    documentElement: {lang},
    querySelectorAll: key => key === '[data-scholar-metric]' ? metrics : [selectors[key]],
    querySelector: key => selectors[key], createElement: node
  };
  vm.runInNewContext(code, {window:{CCML_SCHOLAR:data},document,Date,Number,Array,Math});
  return {metrics,selectors};
}
let result=render(null);
assert.equal(result.selectors['[data-scholar-values]'].hidden,true);
assert.equal(result.selectors['[data-scholar-pending]'].hidden,false);
result=render({author_id:'iqaMS78AAAAJ',updated_at:'2020-01-01T00:00:00Z',citations:120,h_index:4,i10_index:3,graph:[{year:2019,citations:120}]});
assert.equal(result.metrics[0].textContent,'120');
assert.equal(result.selectors['[data-scholar-values]'].hidden,false);
assert.equal(result.selectors['[data-scholar-chart]'].hidden,false);
assert.match(result.selectors['[data-scholar-date]'].textContent,/Update delayed/);
assert.equal(result.selectors['[data-scholar-graph]'].children[0].children[0].children[1].style.height,'85%');
result=render({author_id:'iqaMS78AAAAJ',updated_at:'2020-01-01T00:00:00Z',citations:120,h_index:4,i10_index:3,graph:[{year:2019,citations:120}]},'ko');
assert.match(result.selectors['[data-scholar-date]'].textContent,/전체 기간 · 갱신 2020-01-01 · 갱신 지연/);
assert.equal(result.selectors['[data-scholar-graph]'].children.length,1);
console.log('PASS: first-run fallback, English/Korean metrics, stale date and citation chart.');

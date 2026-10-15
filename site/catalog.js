'use strict';

(() => {
  const controls = document.getElementById('catalog-controls');
  const search = document.getElementById('search');
  const source = document.getElementById('source');
  const count = document.getElementById('result-count');
  const empty = document.getElementById('empty-state');
  const cards = Array.from(document.querySelectorAll('.card'));
  const normalize = text => text.normalize('NFKC').toLocaleLowerCase('ja');

  function update() {
    const query = normalize(search.value.trim());
    let visible = 0;
    for (const card of cards) {
      const matchesTitle = normalize(card.dataset.title).includes(query);
      const matchesSource = source.value === 'all' || card.dataset.source === source.value;
      card.hidden = !(matchesTitle && matchesSource);
      if (!card.hidden) visible += 1;
    }
    count.textContent = `${visible}件 / ${cards.length}件`;
    empty.hidden = visible !== 0;
  }

  // A failed image leaves the neutral thumbnail background visible.
  for (const image of document.querySelectorAll('.thumbnail img')) {
    image.addEventListener('error', () => { image.hidden = true; });
    if (image.complete && image.naturalWidth === 0) image.hidden = true;
  }
  search.addEventListener('input', update);
  source.addEventListener('change', update);
  update();
  controls.hidden = false;
})();

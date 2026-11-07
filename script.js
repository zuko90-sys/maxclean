// Переключатель города и ползунки «до/после»
(function () {
  var CITIES = {
    batumi: {
      ru: 'в Батуми', en: 'Batumi',
      phone: '+995 599 50 91 49', tel: 'tel:+995599509149',
      tg: 'https://t.me/+995599509149',
      ig: 'https://www.instagram.com/max_clean_batumi/'
    },
    tbilisi: {
      ru: 'в Тбилиси', en: 'Tbilisi',
      phone: '+995 595 00 50 71', tel: 'tel:+995595005071',
      tg: 'https://t.me/+995595005071',
      ig: 'https://www.instagram.com/max_clean_tbilisi/'
    }
  };

  function all(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }

  function setCity(key, animate) {
    var c = CITIES[key] || CITIES.batumi;
    all('[data-bind="city-ru"]').forEach(function (el) { el.textContent = c.ru; });
    all('[data-bind="city-en"]').forEach(function (el) { el.textContent = c.en; });
    all('[data-bind="phone"]').forEach(function (el) { el.textContent = c.phone; });
    all('[data-bind="tel"]').forEach(function (el) { el.href = c.tel; });
    all('[data-bind="tg"]').forEach(function (el) { el.href = c.tg; });
    all('[data-bind="ig"]').forEach(function (el) { el.href = c.ig; });
    all('.city__btn').forEach(function (b) {
      b.setAttribute('aria-pressed', b.dataset.city === key ? 'true' : 'false');
    });
    if (animate) {
      var p = document.querySelector('.plaque--hero');
      if (p) { p.classList.remove('is-swapping'); void p.offsetWidth; p.classList.add('is-swapping'); }
    }
    try { localStorage.setItem('mc-city', key); } catch (e) {}
  }

  var saved = null;
  try { saved = localStorage.getItem('mc-city'); } catch (e) {}
  setCity(CITIES[saved] ? saved : 'batumi', false);

  all('.city__btn').forEach(function (b) {
    b.addEventListener('click', function () { setCity(b.dataset.city, true); });
  });

  // До / после
  all('.ba').forEach(function (box) {
    var range = box.querySelector('.ba__range');
    var dragging = false;

    function set(pct) {
      pct = Math.max(0, Math.min(100, pct));
      box.style.setProperty('--pos', pct + '%');
      range.value = Math.round(pct);
    }
    function fromEvent(e) {
      var r = box.getBoundingClientRect();
      set((e.clientX - r.left) / r.width * 100);
    }

    box.addEventListener('pointerdown', function (e) {
      dragging = true;
      box.setPointerCapture(e.pointerId);
      fromEvent(e);
    });
    box.addEventListener('pointermove', function (e) { if (dragging) fromEvent(e); });
    box.addEventListener('pointerup', function () { dragging = false; });
    box.addEventListener('pointercancel', function () { dragging = false; });
    range.addEventListener('input', function () { set(Number(range.value)); });
  });
})();

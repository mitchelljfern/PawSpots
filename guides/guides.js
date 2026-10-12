/* PawSpots park guides: shared behaviour for the hub and every guide page.
   No dependencies. Everything degrades to plain HTML if this fails to load. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---- text size: Aa button cycles normal → large → extra large ---- */
  var SIZES = ['normal', 'large', 'xlarge'];
  function applyText(size) {
    if (size === 'normal') document.documentElement.removeAttribute('data-text');
    else document.documentElement.setAttribute('data-text', size);
    var b = $('#textsize');
    if (b) {
      b.setAttribute('aria-pressed', size === 'normal' ? 'false' : 'true');
      b.setAttribute('aria-label', 'Text size: ' + size.replace('xlarge', 'extra large') + '. Tap to change.');
    }
  }
  var saved = 'normal';
  try { saved = localStorage.getItem('ps-text') || 'normal'; } catch (e) {}
  if (SIZES.indexOf(saved) < 0) saved = 'normal';
  applyText(saved);
  var tsBtn = $('#textsize');
  if (tsBtn) tsBtn.addEventListener('click', function () {
    saved = SIZES[(SIZES.indexOf(saved) + 1) % SIZES.length];
    applyText(saved);
    try { localStorage.setItem('ps-text', saved); } catch (e) {}
    toast(saved === 'normal' ? 'Normal text' : saved === 'large' ? 'Larger text' : 'Largest text');
  });

  /* ---- toast ---- */
  var toastEl = $('#toast'), toastT;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg; toastEl.classList.add('show');
    clearTimeout(toastT); toastT = setTimeout(function () { toastEl.classList.remove('show'); }, 1800);
  }

  /* ---- share: native sheet on phones, copy link elsewhere ---- */
  $$('[data-share]').forEach(function (b) {
    b.addEventListener('click', function () {
      var data = { title: document.title, text: b.getAttribute('data-share') || document.title, url: location.href };
      if (navigator.share) { navigator.share(data).catch(function () {}); return; }
      if (navigator.clipboard) navigator.clipboard.writeText(location.href).then(function () { toast('Link copied'); }, function () { toast(location.href); });
      else toast(location.href);
    });
  });

  /* ---- back to top ---- */
  var top = $('#backtop');
  if (top) {
    var onScroll = function () { top.classList.toggle('show', window.scrollY > 900); };
    window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
    top.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  }

  /* ---- jump nav: highlight the section in view, keep the chip visible ---- */
  var jump = $('.jump');
  if (jump && 'IntersectionObserver' in window) {
    var links = $$('a', jump), byId = {};
    links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
    var current = null;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) current = en.target.id; });
      if (!current || !byId[current]) return;
      links.forEach(function (a) { a.classList.toggle('on', a === byId[current]); });
      var a = byId[current], ul = a.parentNode.parentNode;
      var left = a.offsetLeft - (ul.clientWidth - a.offsetWidth) / 2;
      ul.scrollTo({ left: left, behavior: 'smooth' });
    }, { rootMargin: '-45% 0px -50% 0px' });
    $$('.sec[id]').forEach(function (s) { io.observe(s); });
  }

  /* ---- packing checklist: remember ticks per guide ---- */
  var key = 'ps-check-' + location.pathname;
  var ticked = {};
  try { ticked = JSON.parse(localStorage.getItem(key) || '{}'); } catch (e) {}
  $$('.check input').forEach(function (c, i) {
    if (ticked[i]) c.checked = true;
    c.addEventListener('change', function () {
      ticked[i] = c.checked;
      try { localStorage.setItem(key, JSON.stringify(ticked)); } catch (e) {}
    });
  });

  /* ---- hub: search, type filter and sort ---- */
  var grid = $('#grid');
  if (grid) {
    var cards = $$('.gcard', grid).map(function (a) {
      return { el: a.parentNode, hay: (a.getAttribute('data-hay') || '').toLowerCase(), type: a.getAttribute('data-type'),
               score: +a.getAttribute('data-score'), name: a.getAttribute('data-name') };
    });
    var q = $('#q'), clear = $('#qclear'), countEl = $('#count'), empty = $('#empty'), sort = $('#sort');
    var type = 'all';
    function params() {
      try {
        var p = new URLSearchParams(location.search);
        if (p.get('type')) type = p.get('type');
        if (p.get('q') && q) q.value = p.get('q');
      } catch (e) {}
    }
    function render() {
      var text = (q ? q.value : '').trim().toLowerCase();
      var words = text ? text.split(/\s+/) : [];
      var shown = 0;
      var order = cards.slice().sort(function (a, b) {
        if (sort && sort.value === 'score') return b.score - a.score || a.name.localeCompare(b.name);
        return a.name.localeCompare(b.name);
      });
      order.forEach(function (c) {
        var ok = (type === 'all' || c.type === type) && words.every(function (w) { return c.hay.indexOf(w) >= 0; });
        c.el.hidden = !ok; if (ok) shown++;
        grid.appendChild(c.el);
      });
      if (countEl) countEl.textContent = shown === cards.length ? 'All ' + shown + ' guides' : shown + ' of ' + cards.length + ' guides';
      if (empty) empty.hidden = shown > 0;
      if (clear) clear.hidden = !text;
      $$('.chip[data-type]').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-type') === type ? 'true' : 'false'); });
      try {
        var u = new URL(location.href);
        if (type === 'all') u.searchParams.delete('type'); else u.searchParams.set('type', type);
        if (text) u.searchParams.set('q', text); else u.searchParams.delete('q');
        history.replaceState(null, '', u);
      } catch (e) {}
    }
    params();
    if (q) q.addEventListener('input', render);
    if (clear) clear.addEventListener('click', function () { q.value = ''; q.focus(); render(); });
    if (sort) sort.addEventListener('change', render);
    $$('.chip[data-type]').forEach(function (b) { b.addEventListener('click', function () { type = b.getAttribute('data-type'); render(); }); });
    render();
  }
})();

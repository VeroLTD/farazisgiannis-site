// farazisgiannis.com — home page (25 Nov 2026): rows of cards that scroll sideways, the tabbed section, and for
// Christmas 2026 the «24 πόρτες» calendar, the hero's film of the day and a little gold dust in the hero.
// No cookies, no storage, nothing sent anywhere.
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var el = document.documentElement.lang === 'el';
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var save = navigator.connection && navigator.connection.saveData;
  var ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  // ---- the row of joined boxes: five sections open one at a time under the box that is pressed (26 Nov 2026)
  (function () {
    var deck = $('[data-deck]'); if (!deck) return;
    var tabs = $$('.deck__tab', deck).filter(function (t) { return document.getElementById(t.getAttribute('aria-controls')); });
    if (tabs.length < 2) return;
    var bar = $('.deck__tabs', deck);
    tabs.forEach(function (t) { var p = document.getElementById(t.getAttribute('aria-controls')); p.setAttribute('role', 'tabpanel'); p.setAttribute('aria-labelledby', t.id); });
    function open(t, quiet) {
      var swap = function () {
        tabs.forEach(function (x) { var on = x === t; x.setAttribute('aria-selected', on ? 'true' : 'false'); x.tabIndex = on || (!t && x === tabs[0]) ? 0 : -1; document.getElementById(x.getAttribute('aria-controls')).hidden = !on; });
        window.dispatchEvent(new Event('resize'));
        if (t && bar.scrollWidth > bar.clientWidth + 4) bar.scrollTo({ left: t.offsetLeft - (bar.clientWidth - t.offsetWidth) / 2, behavior: quiet || still ? 'auto' : 'smooth' });
      };
      if (!quiet && document.startViewTransition && !still) document.startViewTransition(swap); else swap();
    }
    deck.addEventListener('click', function (e) { var t = e.target.closest && e.target.closest('.deck__tab'); if (t) open(t.getAttribute('aria-selected') === 'true' ? null : t); });
    deck.addEventListener('keydown', function (e) {
      var i = tabs.indexOf(document.activeElement); if (i < 0) return;
      var j = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 : e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : null;
      if (j === null) return; e.preventDefault(); j = (j + tabs.length) % tabs.length; tabs[j].focus(); open(tabs[j]);
    });
    // an address that points inside a closed section opens it first
    function byHash() {
      var h = location.hash.slice(1), el2 = h && document.getElementById(h), p = el2 && el2.closest('[data-deck-panel]');
      if (p && p.hidden) { open(document.getElementById(p.getAttribute('aria-labelledby')), true); el2.scrollIntoView(); }
    }
    window.addEventListener('hashchange', byHash);
    deck.hidden = false; open(tabs[0], true); byHash();
  })();

  // ---- rows that scroll sideways
  $$('[data-rail]').forEach(function (rail) {
    var list = $('ul', rail); if (!list) return;
    var nav = document.createElement('div'); nav.className = 'rail__nav';
    var prev = document.createElement('button'), next = document.createElement('button');
    prev.type = next.type = 'button';
    prev.className = 'rail__btn rail__btn--prev'; next.className = 'rail__btn rail__btn--next';
    prev.setAttribute('aria-label', el ? 'Προηγούμενα' : 'Previous'); next.setAttribute('aria-label', el ? 'Επόμενα' : 'Next');
    prev.innerHTML = next.innerHTML = ARROW;
    nav.appendChild(prev); nav.appendChild(next); rail.insertBefore(nav, list);
    var bar = document.createElement('div'); bar.className = 'rail__bar'; bar.setAttribute('aria-hidden', 'true'); bar.innerHTML = '<i></i>'; rail.appendChild(bar);
    var thumb = bar.firstChild;
    function sync() {
      var max = list.scrollWidth - list.clientWidth, x = list.scrollLeft;
      prev.disabled = x < 4; next.disabled = x > max - 4;
      nav.hidden = bar.hidden = max < 8;
      var w = Math.max(.15, list.clientWidth / list.scrollWidth);
      thumb.style.width = (w * 100) + '%';
      thumb.style.transform = 'translateX(' + ((max > 0 ? x / max : 0) * (1 - w) / w * 100) + '%)';
    }
    function go(dir) { list.scrollBy({ left: dir * list.clientWidth * .9, behavior: still ? 'auto' : 'smooth' }); }
    prev.addEventListener('click', function () { go(-1); }); next.addEventListener('click', function () { go(1); });
    list.addEventListener('scroll', sync, { passive: true }); window.addEventListener('resize', sync); sync();
  });

  // ---- tabs
  $$('[data-tabs]').forEach(function (box, bi) {
    var vt = 'tabs-' + bi;
    var tabs = $$('[role="tab"]', box), panels = $$('[role="tabpanel"]', box);
    if (!tabs.length) return;
    box.classList.add('is-js');
    function set(i) { tabs.forEach(function (t, n) { t.setAttribute('aria-selected', n === i ? 'true' : 'false'); t.tabIndex = n === i ? 0 : -1; panels[n].hidden = n !== i; panels[n].style.viewTransitionName = n === i ? vt : ''; }); }
    function show(i, focus, first) {
      if (!first && document.startViewTransition && !still) document.startViewTransition(function () { set(i); }); else set(i);
      if (focus) tabs[i].focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { show(i); });
      t.addEventListener('keydown', function (e) {
        var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (d) { e.preventDefault(); show((i + d + tabs.length) % tabs.length, true); }
      });
    });
    show(0, false, true);
  });

  // ---- gold dust in the hero (decorative; never for visitors who ask for less motion)
  (function () {
    var c = $('.xmas-dust'); if (!c || still || !c.getContext) return;
    var g = c.getContext('2d'), W = 0, H = 0, P = [], on = false, raf = 0, last = 0;
    function size() {
      var r = c.getBoundingClientRect(), d = Math.min(window.devicePixelRatio || 1, 2);
      W = r.width; H = r.height; c.width = W * d; c.height = H * d; g.setTransform(d, 0, 0, d, 0, 0);
      var n = Math.round(Math.min(90, W * H / 14000)); P = [];
      for (var i = 0; i < n; i++) P.push({ x: Math.random() * W, y: Math.random() * H, r: .6 + Math.random() * 1.7, v: 8 + Math.random() * 22, s: 6 + Math.random() * 18, p: Math.random() * 6.28, t: 1 + Math.random() * 2.5 });
    }
    function draw(ts) {
      var dt = Math.min(.05, (ts - last) / 1000 || 0), t = ts / 1000; last = ts;
      g.clearRect(0, 0, W, H);
      for (var i = 0; i < P.length; i++) {
        var p = P[i]; p.y += p.v * dt; if (p.y > H + 4) { p.y = -4; p.x = Math.random() * W; }
        var x = p.x + Math.sin(t * .5 + p.p) * p.s, a = .35 + .45 * (0.5 + 0.5 * Math.sin(t * p.t + p.p));
        g.fillStyle = 'rgba(246,214,150,' + a.toFixed(3) + ')';
        g.beginPath(); g.arc(x, p.y, p.r, 0, 6.2832); g.fill();
      }
      if (on) raf = requestAnimationFrame(draw);
    }
    function run(v) { if (v && !on) { on = true; last = performance.now(); raf = requestAnimationFrame(draw); } else if (!v && on) { on = false; cancelAnimationFrame(raf); } }
    size(); window.addEventListener('resize', size);
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { run(es[0].isIntersecting && !document.hidden); }).observe(c); else run(true);
    document.addEventListener('visibilitychange', function () { if (document.hidden) run(false); else run(true); });
  })();

  // ---- 24 doors
  var dataEl = $('#doors-data'); if (!dataEl) return;
  var data; try { data = JSON.parse(dataEl.textContent); } catch (e) { return; }
  var byDay = {}; (data.days || []).forEach(function (r) { byDay[r.d] = r; });
  var poster0 = $('.today__poster'), base = poster0 ? poster0.getAttribute('src').replace(/door-closed\.jpg.*$/, '') : '/assets/xmas/';
  var now = Date.now();
  if (data.preview) {   // the owner's preview only: ?day=7 shows the page as it will be once door 7 has opened
    var m = /[?&]day=(\d+)/.exec(location.search); if (m) now = Date.UTC(2026, 11, Math.min(31, +m[1]), 16, 0, 1);
  }
  function opensAt(d) { return d === 25 ? Date.UTC(2026, 11, 25, 7, 0, 0) : Date.UTC(2026, 11, d, 16, 0, 0); }   // 18:00 / 09:00 Cyprus time
  function isOpen(d) { return now >= opensAt(d); }
  var latest = 0;
  for (var d = 1; d <= 24; d++) if (isOpen(d) && byDay[d]) latest = d;
  function two(n) { return (n < 10 ? '0' : '') + n; }
  function left(d) { var n = 25 - d; return n === 1 ? 'αύριο Χριστούγεννα' : n + ' μέρες ως τα Χριστούγεννα'; }

  var dlg = $('#door-dialog'), dv = dlg && $('video', dlg);
  function openDoor(d, from) {
    var r = byDay[d], film = d === 25;
    if (!film && !r) return;
    var src = base + (film ? 'liga-vimata-piso.mp4' : 'porta-' + two(d) + '.mp4');
    if (!dlg || !dlg.showModal) { location.href = src; return; }
    $('#door-dialog-k').textContent = film ? '25 Δεκεμβρίου · Η ταινία' : 'Πόρτα ' + d + ' · ' + left(d);
    $('#door-dialog-t').textContent = film ? '«Λίγα βήματα πίσω»' : '«' + r.p + '»';
    $('#door-dialog-th').textContent = film ? 'Κάποιος πρέπει να στέκεται λίγα βήματα πίσω. Καλά Χριστούγεννα.' : r.t;
    dv.poster = film ? base + 'liga-vimata-piso.jpg' : base + 'porta-' + two(d) + '.jpg';
    dv.src = src; dv.muted = false;
    var tile = from && $('.door__in img', from);
    var show = function () { if (tile) tile.style.viewTransitionName = ''; dv.style.viewTransitionName = 'door-film'; dlg.showModal(); };
    if (tile && document.startViewTransition && !still) {
      tile.style.viewTransitionName = 'door-film';
      var vt = document.startViewTransition(show);
      vt.finished.then(function () { dv.style.viewTransitionName = ''; }, function () {});
    } else { show(); dv.style.viewTransitionName = ''; }
    var p = dv.play(); if (p && p.catch) p.catch(function () {});
  }
  if (dlg) {
    dlg.addEventListener('close', function () { dv.pause(); dv.removeAttribute('src'); dv.load(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    $('.door-dialog__x', dlg).addEventListener('click', function () { dlg.close(); });
  }
  // a closed door answers a knock: it shakes and says when it opens
  var DAYS = ['την Κυριακή', 'τη Δευτέρα', 'την Τρίτη', 'την Τετάρτη', 'την Πέμπτη', 'την Παρασκευή', 'το Σάββατο'];
  var sec = $('#portes'), wrap = sec && $('.wrap', sec), bubble, bubbleT;
  function knock(b, d) {
    if (!still) { b.classList.remove('is-knock'); void b.offsetWidth; b.classList.add('is-knock'); }
    if (!bubble) { bubble = document.createElement('p'); bubble.className = 'door-bubble'; bubble.setAttribute('role', 'status'); wrap.appendChild(bubble); }
    var when = DAYS[new Date(Date.UTC(2026, 11, d, 12)).getUTCDay()] + ' ' + d + ' Δεκεμβρίου, ' + (d === 25 ? 'στις 9 το πρωί' : 'στις 6 το απόγευμα');
    bubble.innerHTML = '<b>Τοκ, τοκ…</b>' + (d === 25 ? 'Η ταινία έρχεται ' : 'Ανοίγει ') + when + '.';
    var r = b.getBoundingClientRect(), w = wrap.getBoundingClientRect(), cx = r.left + r.width / 2 - w.left;
    var half = Math.min(150, w.width * .39), x = Math.max(half + 4, Math.min(w.width - half - 4, cx));
    bubble.style.left = x + 'px'; bubble.style.top = (r.top - w.top) + 'px'; bubble.style.setProperty('--ax', (50 + (cx - x) / (2 * half) * 100) + '%');
    bubble.classList.add('is-on'); clearTimeout(bubbleT); bubbleT = setTimeout(function () { bubble.classList.remove('is-on'); }, 3200);
  }
  // the time left to the next door, counted every second (real time only, never the preview's ?day=)
  (function () {
    var box = $('#doors-next'); if (!box) return;
    var next = 0; for (var d = 1; d <= 25; d++) if (!isOpen(d)) { next = d; break; }
    if (!next) return;
    var lab = $('.doors__next-l', box), cells = $$('.doors__clock b', box);
    lab.textContent = next === 25 ? 'Η ταινία σε' : (next === 1 ? 'Η πρώτη πόρτα ανοίγει σε' : 'Η επόμενη πόρτα ανοίγει σε');
    function tick() {
      var ms = opensAt(next) - (now + (Date.now() - t0)); if (ms <= 0) { location.reload(); return; }
      var s = Math.floor(ms / 1000), v = [Math.floor(s / 86400), Math.floor(s % 86400 / 3600), Math.floor(s % 3600 / 60), s % 60];
      for (var i = 0; i < 4; i++) cells[i].textContent = two(v[i]);
    }
    var t0 = Date.now(); box.hidden = false; tick();
    setInterval(function () { if (!document.hidden) tick(); }, 1000);
  })();

  $$('.door').forEach(function (b, i) {
    var d = +b.getAttribute('data-d');
    if (d === 25) {
      if (isOpen(25) && data.film) { b.disabled = false; b.classList.add('is-open'); b.addEventListener('click', function () { openDoor(25); }); }
      else { b.disabled = false; b.setAttribute('aria-disabled', 'true'); b.addEventListener('click', function () { knock(b, 25); }); }
      return;
    }
    if (!isOpen(d)) { b.disabled = false; b.setAttribute('aria-disabled', 'true'); b.addEventListener('click', function () { knock(b, d); }); return; }
    var ready = !!byDay[d];
    setTimeout(function () { b.classList.add('is-open'); if (d === latest) b.classList.add('is-today'); }, still ? 0 : 250 + i * 70);
    if (ready) {
      b.disabled = false;
      b.setAttribute('aria-label', 'Πόρτα ' + d + ' · δείτε το βίντεο και τη σκέψη της ημέρας');
      b.addEventListener('click', function () { openDoor(d, b); });
    }
  });
  // the doors are one row: the last door that opened is brought to the middle; two arrows go back and forth
  (function () {
    var row = $('.doors'), rail = $('.doors-rail'); if (!row || !rail) return;
    var mid = function (li, smooth) { var to = li.offsetLeft - (row.clientWidth - li.offsetWidth) / 2; if (smooth && row.scrollTo) row.scrollTo({ left: to, behavior: 'smooth' }); else row.scrollLeft = to; };
    var at = $('.door[data-d="' + (latest || 1) + '"]', row); if (at && latest) mid(at.parentNode, false);
    var nav = document.createElement('div'); nav.className = 'doors-rail__nav';
    [-1, 1].forEach(function (dir) { var b = document.createElement('button'); b.type = 'button'; b.setAttribute('data-dir', dir); b.setAttribute('aria-label', rail.getAttribute(dir < 0 ? 'data-prev' : 'data-next') || ''); nav.appendChild(b); });
    rail.appendChild(nav);
    var sync = function () { nav.firstChild.disabled = row.scrollLeft < 8; nav.lastChild.disabled = row.scrollLeft > row.scrollWidth - row.clientWidth - 8; };
    nav.addEventListener('click', function (e) { var b = e.target.closest && e.target.closest('button'); if (b) row.scrollBy({ left: +b.getAttribute('data-dir') * row.clientWidth * .66, behavior: still ? 'auto' : 'smooth' }); });
    row.addEventListener('scroll', sync, { passive: true }); window.addEventListener('resize', sync); sync();
  })();

  var status = $('#doors-status'), line = $('#today-line');
  if (latest) {
    var txt = isOpen(25) ? 'Καλά Χριστούγεννα! Και οι 24 πόρτες είναι ανοιχτές.' : 'Σήμερα: πόρτα ' + latest + ' · ' + left(latest) + '. Πατήστε μια ανοιχτή πόρτα.';
    if (status) status.textContent = txt;
    if (line) line.textContent = 'Πόρτα ' + latest + ' · «' + byDay[latest].p + '»';
  } else if (status) {
    var days = Math.ceil((opensAt(1) - now) / 864e5);
    if (days > 1) status.textContent = 'Η πρώτη πόρτα ανοίγει την Τρίτη 1 Δεκεμβρίου, στις 6 το απόγευμα — σε ' + days + ' μέρες.';
  }

  // ---- the hero's film of the day: the latest open door, silent until the visitor asks for sound
  var today = $('#today');
  if (today && !latest) today.addEventListener('click', function (e) { if (e.target.closest && e.target.closest('a')) return; var s = $('#portes'); if (s) s.scrollIntoView({ behavior: still ? 'auto' : 'smooth' }); });
  if (today && latest) {
    var tv = $('.today__video', today), snd = $('.today__sound', today), img = $('.today__poster', today);
    var stem = base + 'porta-' + two(latest);
    img.src = stem + '.jpg'; img.alt = 'Το βίντεο της ημέρας: «' + byDay[latest].p + '»';
    tv.poster = stem + '.jpg';
    var started = false;
    function start() { if (started) return; started = true; tv.src = stem + '.mp4'; tv.hidden = false; }
    function play() { start(); var p = tv.play(); if (p && p.catch) p.catch(function () {}); }
    snd.hidden = false;
    today.addEventListener('click', function (e) { if (e.target === snd || (e.target.closest && e.target.closest('a'))) return; tv.pause(); openDoor(latest, $('.door[data-d="' + latest + '"]')); });
    snd.addEventListener('click', function () {
      var onNow = tv.muted;   // turning sound on
      tv.muted = !onNow; snd.setAttribute('aria-pressed', onNow ? 'true' : 'false');
      snd.textContent = onNow ? snd.getAttribute('data-on') : snd.getAttribute('data-off');
      if (onNow) { start(); tv.currentTime = 0; play(); }
    });
    if (!still && !save && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { if (es[0].isIntersecting) play(); else if (started) tv.pause(); }, { threshold: .35 }).observe(today);
    }
  }
})();

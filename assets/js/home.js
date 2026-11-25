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
  $$('[data-tabs]').forEach(function (box) {
    var tabs = $$('[role="tab"]', box), panels = $$('[role="tabpanel"]', box);
    if (!tabs.length) return;
    box.classList.add('is-js');
    function show(i, focus) {
      tabs.forEach(function (t, n) { t.setAttribute('aria-selected', n === i ? 'true' : 'false'); t.tabIndex = n === i ? 0 : -1; panels[n].hidden = n !== i; });
      if (focus) tabs[i].focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { show(i); });
      t.addEventListener('keydown', function (e) {
        var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (d) { e.preventDefault(); show((i + d + tabs.length) % tabs.length, true); }
      });
    });
    show(0);
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
  function openDoor(d) {
    var r = byDay[d], film = d === 25;
    if (!film && !r) return;
    var src = base + (film ? 'liga-vimata-piso.mp4' : 'porta-' + two(d) + '.mp4');
    if (!dlg || !dlg.showModal) { location.href = src; return; }
    $('#door-dialog-k').textContent = film ? '25 Δεκεμβρίου · Η ταινία' : 'Πόρτα ' + d + ' · ' + left(d);
    $('#door-dialog-t').textContent = film ? '«Λίγα βήματα πίσω»' : '«' + r.p + '»';
    $('#door-dialog-th').textContent = film ? 'Κάποιος πρέπει να στέκεται λίγα βήματα πίσω. Καλά Χριστούγεννα.' : r.t;
    dv.poster = film ? base + 'liga-vimata-piso.jpg' : base + 'porta-' + two(d) + '.jpg';
    dv.src = src; dv.muted = false;
    dlg.showModal();
    var p = dv.play(); if (p && p.catch) p.catch(function () {});
  }
  if (dlg) {
    dlg.addEventListener('close', function () { dv.pause(); dv.removeAttribute('src'); dv.load(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    $('.door-dialog__x', dlg).addEventListener('click', function () { dlg.close(); });
  }
  $$('.door').forEach(function (b, i) {
    var d = +b.getAttribute('data-d');
    if (d === 25) {
      if (isOpen(25) && data.film) { b.disabled = false; b.classList.add('is-open'); b.addEventListener('click', function () { openDoor(25); }); }
      return;
    }
    if (!isOpen(d)) return;
    var ready = !!byDay[d];
    setTimeout(function () { b.classList.add('is-open'); if (d === latest) b.classList.add('is-today'); }, still ? 0 : 250 + i * 70);
    if (ready) {
      b.disabled = false;
      b.setAttribute('aria-label', 'Πόρτα ' + d + ' · δείτε το βίντεο και τη σκέψη της ημέρας');
      b.addEventListener('click', function () { openDoor(d); });
    }
  });
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
  if (today && latest) {
    var tv = $('.today__video', today), snd = $('.today__sound', today), img = $('.today__poster', today);
    var stem = base + 'porta-' + two(latest);
    img.src = stem + '.jpg'; img.alt = 'Το βίντεο της ημέρας: «' + byDay[latest].p + '»';
    tv.poster = stem + '.jpg';
    var started = false;
    function start() { if (started) return; started = true; tv.src = stem + '.mp4'; tv.hidden = false; }
    function play() { start(); var p = tv.play(); if (p && p.catch) p.catch(function () {}); }
    snd.hidden = false;
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

// farazisgiannis.com — small touches on every page (25 Nov 2026): the header gets smaller once the page has moved,
// cards are lit where the pointer is, and at Christmas the hat and the lights answer a tap. No cookies, no storage.
(function () {
  'use strict';
  var head = document.querySelector('.site-head');
  if (head) {
    var stuck = false;
    var onScroll = function () { var s = window.scrollY > 24; if (s !== stuck) { stuck = s; head.classList.toggle('is-stuck', s); } };
    window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  }
  // the light on cards, doors and the film of the day: where the pointer is, as --mx / --my
  if (window.matchMedia && window.matchMedia('(hover: hover)').matches) {
    document.addEventListener('pointermove', function (e) {
      var band = e.target.closest && e.target.closest('.hero, .page-head, .doors-sec');
      if (band) { var b = band.getBoundingClientRect(); band.style.setProperty('--lx', (e.clientX - b.left).toFixed(0) + 'px'); band.style.setProperty('--ly', (e.clientY - b.top).toFixed(0) + 'px'); band.classList.add('is-lit'); }
      var t = e.target.closest && e.target.closest('.card, .lcards a, .door, .today__frame');
      if (!t) return;
      var r = t.getBoundingClientRect();
      t.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100).toFixed(1) + '%');
      t.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100).toFixed(1) + '%');
      t.style.setProperty('--tx', ((e.clientX - r.left) / r.width - .5).toFixed(3));
      t.style.setProperty('--ty', ((e.clientY - r.top) / r.height - .5).toFixed(3));
    }, { passive: true });
  }
  // Christmas: the hat nods when touched, a bulb goes out and comes back when tapped
  [].forEach.call(document.querySelectorAll('.xmas-hat'), function (h) {
    var go = function () { h.classList.remove('is-nod'); void h.getBoundingClientRect(); h.classList.add('is-nod'); };
    h.parentNode.addEventListener('pointerenter', go);
  });
  var lights = document.querySelector('.xmas-lights');
  if (lights) lights.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('.xl'); if (b) b.classList.toggle('is-off');
  });
})();

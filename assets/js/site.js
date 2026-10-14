// farazisgiannis.com — the phone menu and the contact form. No tracking, no third-party code.
(function () {
  var btn = document.querySelector('.menu-btn'), nav = document.getElementById('nav');
  if (btn && nav) btn.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  var form = document.getElementById('enquiry');
  if (!form) return;
  var lang = form.getAttribute('data-lang') || 'el', el = lang === 'el';
  var msg = {
    missing: el ? 'Γράψτε το όνομά σας και ένα τηλέφωνο ή e-mail για να σας απαντήσω.' : 'Please give your name and a phone number or e-mail so I can reply.',
    email: el ? 'Το e-mail δεν φαίνεται σωστό. Ελέγξτε το και ξαναδοκιμάστε.' : 'That e-mail address does not look right. Please check it.',
    phone: el ? 'Το τηλέφωνο δεν φαίνεται σωστό. Χρησιμοποιήστε μόνο αριθμούς, κενά και +.' : 'That phone number does not look right. Use only digits, spaces and +.',
    consent: el ? 'Τσεκάρετε τη συγκατάθεση ώστε να μπορώ να επικοινωνήσω μαζί σας.' : 'Please tick the consent box so I can contact you.',
    rate_limited: el ? 'Έχουν σταλεί πολλά μηνύματα. Δοκιμάστε ξανά σε μία ώρα ή καλέστε στο +357 97 840941.' : 'Too many messages have been sent. Try again in an hour or call +357 97 840941.',
    failed: el ? 'Το μήνυμα δεν στάλθηκε. Καλέστε στο +357 97 840941 ή στείλτε μήνυμα στο WhatsApp.' : 'The message was not sent. Please call +357 97 840941 or send a WhatsApp message.',
    ok: el ? 'Ευχαριστώ. Το μήνυμά σας στάλθηκε και θα σας καλέσω σύντομα.' : 'Thank you. Your message has been sent and I will call you soon.',
    sending: el ? 'Αποστολή…' : 'Sending…',
  };
  if (lang === 'ru') msg = {
    missing: 'Укажите имя и телефон или e-mail, чтобы я мог ответить.',
    email: 'Похоже, e-mail указан неверно. Проверьте его.',
    phone: 'Похоже, телефон указан неверно. Используйте только цифры, пробелы и +.',
    consent: 'Отметьте согласие, чтобы я мог с вами связаться.',
    rate_limited: 'Отправлено слишком много сообщений. Попробуйте через час или позвоните по номеру +357 97 840941.',
    failed: 'Сообщение не отправлено. Позвоните по номеру +357 97 840941 или напишите в WhatsApp.',
    ok: 'Спасибо. Ваше сообщение отправлено, я скоро перезвоню.',
    sending: 'Отправляем…',
  };
  var status = form.querySelector('.status'), submit = form.querySelector('button[type=submit]');
  function show(kind, text) { status.className = 'status ' + kind; status.textContent = text; }
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var f = form.elements;
    var data = {
      name: f.name.value.trim(), phone: f.phone.value.trim(), email: f.email.value.trim(), topic: f.topic.value,
      message: f.message.value.trim(), website: f.website.value, consent: f.consent.checked, lang: lang,
    };
    if (!data.name || (!data.phone && !data.email)) return show('err', msg.missing);
    if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(data.email)) return show('err', msg.email);
    if (data.phone && !/^[+()\d\s.-]{6,40}$/.test(data.phone)) return show('err', msg.phone);
    if (!data.consent) return show('err', msg.consent);
    var label = submit.textContent; submit.disabled = true; submit.textContent = msg.sending;
    fetch(form.action, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (b) { return { ok: r.ok, b: b }; }); })
      .then(function (r) {
        if (r.ok) { form.reset(); show('ok', msg.ok); }
        else show('err', msg[r.b && r.b.error] || msg.failed);
      })
      .catch(function () { show('err', msg.failed); })
      .then(function () { submit.disabled = false; submit.textContent = label; });
  });
})();

// Short silent videos (11 Oct 2026): they play only while on screen, never for visitors who ask for less motion or to
// save data (then the first frame stays), and a button pauses or resumes each one. Nothing is loaded before that.
(function () {
  var films = [].slice.call(document.querySelectorAll('.film'));
  if (!films.length || !('IntersectionObserver' in window)) return;
  var still = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  var save = navigator.connection && navigator.connection.saveData;
  if (still.matches || save) return;
  films.forEach(function (f) {
    var v = f.querySelector('video'), b = f.querySelector('.film__toggle'), paused = false, visible = false;
    if (!v || !b) return;
    function run() { if (visible && !paused && !still.matches) { v.preload = 'auto'; var p = v.play(); if (p && p.catch) p.catch(function () {}); } else v.pause(); }
    b.hidden = false;
    b.addEventListener('click', function () {
      paused = !paused;
      f.classList.toggle('is-paused', paused);
      b.setAttribute('aria-label', paused ? b.getAttribute('data-play') : b.getAttribute('data-pause'));
      run();
    });
    new IntersectionObserver(function (entries) { entries.forEach(function (e) { visible = e.isIntersecting; run(); }); }, { threshold: 0.2 }).observe(f);
  });
  if (still.addEventListener) still.addEventListener('change', function () { films.forEach(function (f) { var v = f.querySelector('video'); if (v && still.matches) v.pause(); }); });
})();

// Narrated explainer films (11 Oct 2026): poster and a large play button until the visitor starts one, then the player's
// own controls; one film plays at a time. Without this script the films still play with their own controls.
(function () {
  var all = [].slice.call(document.querySelectorAll('.explainer'));
  all.forEach(function (f) {
    var v = f.querySelector('video'), b = f.querySelector('.explainer__play');
    if (!v || !b) return;
    var started = false;
    function start() { started = true; v.controls = true; var p = v.play(); if (p && p.catch) p.catch(function () { b.hidden = false; }); v.focus({ preventScroll: true }); }
    b.hidden = false; v.controls = false;
    b.addEventListener('click', start);
    v.addEventListener('click', function () { if (!started) start(); });
    v.addEventListener('play', function () {
      b.hidden = true;
      all.forEach(function (o) { var ov = o.querySelector('video'); if (ov && ov !== v && !ov.paused) ov.pause(); });
    });
    v.addEventListener('ended', function () { b.hidden = false; });
  });
})();

// «Print» buttons (no inline scripts). Print views (14 Oct 2026): every answer opens for printing, and «Print» on one life
// event prints that event only; everything goes back as it was afterwards.
(function () {
  [].forEach.call(document.querySelectorAll('[data-print]'), function (b) { b.addEventListener('click', function () { window.print(); }); });
  [].forEach.call(document.querySelectorAll('[data-print-one]'), function (b) {
    b.addEventListener('click', function () {
      var t = document.getElementById(b.getAttribute('data-print-one'));
      if (!t) return window.print();
      document.body.classList.add('print-one'); t.classList.add('is-printing');
      window.print();
    });
  });
  var closed = [];
  window.addEventListener('beforeprint', function () {
    closed = [].filter.call(document.querySelectorAll('details.qa:not([open])'), function (d) { d.open = true; return true; });
  });
  window.addEventListener('afterprint', function () {
    closed.forEach(function (d) { d.open = false; }); closed = [];
    document.body.classList.remove('print-one');
    [].forEach.call(document.querySelectorAll('.is-printing'), function (e) { e.classList.remove('is-printing'); });
  });
})();

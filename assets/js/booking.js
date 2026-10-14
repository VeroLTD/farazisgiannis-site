// farazisgiannis.com — online booking (ideas track 2, 14 Oct 2026).
// The calendar IS avrastro.com's: free times and the booking itself go through avrastro.com's booking endpoints, so a
// time taken here, on avrastro.com, in the CRM or in Outlook is taken everywhere. Nothing is stored in this browser,
// no cookies are sent (credentials: 'omit'), no third-party code. Without JavaScript the page links to avrastro.com.
(function () {
  var root = document.getElementById('booking');
  if (!root || !window.fetch) return;
  // Russian edition (14 Oct 2026): the booking system speaks Greek and English, so a Russian page asks in English and
  // shows its own Russian labels; the e-mails then come in English.
  var PAGE_LANG = root.getAttribute('data-lang') || 'el', RU = PAGE_LANG === 'ru';
  var API = root.getAttribute('data-api'), el = PAGE_LANG === 'el', LANG = el ? 'el' : 'en';
  var LOCALE = RU ? 'ru-RU' : el ? 'el-GR' : 'en-GB', TZ = 'Europe/Nicosia';
  var txt = {
    loading: el ? 'Φόρτωση ελεύθερων ωρών…' : 'Loading free times…',
    none: el ? 'Δεν υπάρχουν ελεύθερες ώρες τις επόμενες εβδομάδες. Καλέστε στο +357 97 840941 ή στείλτε μήνυμα.' : 'There are no free times in the coming weeks. Please call +357 97 840941 or send a message.',
    off: el ? 'Η online κράτηση δεν είναι διαθέσιμη αυτή τη στιγμή. Καλέστε στο +357 97 840941.' : 'Online booking is not available right now. Please call +357 97 840941.',
    down: el ? 'Δεν ήταν δυνατό να φορτωθούν οι ώρες. Δοκιμάστε ξανά σε λίγο ή καλέστε στο +357 97 840941.' : 'The times could not be loaded. Please try again shortly or call +357 97 840941.',
    pickDay: el ? 'Διαλέξτε πρώτα ημέρα.' : 'Choose a day first.',
    noSlots: el ? 'Δεν έμειναν ώρες αυτή την ημέρα. Διαλέξτε άλλη.' : 'No times left on this day. Please choose another.',
    slots: el ? 'ώρες' : 'times', slot1: el ? 'ώρα' : 'time',
    missing: el ? 'Συμπληρώστε ονοματεπώνυμο και e-mail, διαλέξτε ημέρα και ώρα και τσεκάρετε τη συγκατάθεση.' : 'Please fill in your name and e-mail, choose a day and a time, and tick the consent box.',
    email: el ? 'Το e-mail δεν φαίνεται σωστό. Εκεί θα σταλεί η επιβεβαίωση.' : 'That e-mail address does not look right. The confirmation is sent there.',
    taken: el ? 'Η ώρα μόλις κλείστηκε από κάποιον άλλον. Διαλέξτε άλλη ώρα.' : 'That time was just taken. Please choose another time.',
    rate: el ? 'Έχουν γίνει πολλά αιτήματα. Δοκιμάστε ξανά σε μία ώρα ή καλέστε στο +357 97 840941.' : 'Too many requests. Try again in an hour or call +357 97 840941.',
    failed: el ? 'Η κράτηση δεν ολοκληρώθηκε. Καλέστε στο +357 97 840941 ή στείλτε μήνυμα στο WhatsApp.' : 'The booking did not go through. Please call +357 97 840941 or send a WhatsApp message.',
    sending: el ? 'Αποστολή…' : 'Sending…',
    okTitle: el ? 'Το αίτημα ραντεβού στάλθηκε' : 'Your appointment request has been sent',
    okBody: el ? 'Θα λάβετε τώρα e-mail ότι το αίτημα παραλήφθηκε και, μόλις το επιβεβαιώσω, δεύτερο e-mail με όλες τις λεπτομέρειες (πού, πώς, προσθήκη στο ημερολόγιο). Αν χρειαστεί, μπορείτε να το ακυρώσετε από τον σύνδεσμο στο e-mail και να κλείσετε άλλη ώρα.' : 'You will now receive an e-mail that the request was received and, once I confirm it, a second e-mail with all the details (where, how, add to your calendar). If you need to, you can cancel it from the link in the e-mail and book another time.',
    again: el ? 'Νέο ραντεβού' : 'Book another',
    place: el ? 'Γράψτε πού θα γίνει η συνάντηση (καφέ και περιοχή, ή διεύθυνση).' : 'Please write where we meet (café and area, or address).',
    partner: el ? 'Τσεκάρετε ότι συμφωνείτε να δοθούν τα στοιχεία σας στον συνεργάτη γενικού κλάδου.' : 'Please tick that you agree your details go to the general-insurance partner.',
  };  if (RU) txt = {
    loading: 'Загружаем свободное время…',
    none: 'В ближайшие недели нет свободного времени. Позвоните по номеру +357 97 840941 или напишите нам.',
    off: 'Онлайн-запись сейчас недоступна. Позвоните по номеру +357 97 840941.',
    down: 'Не удалось загрузить время. Попробуйте позже или позвоните по номеру +357 97 840941.',
    pickDay: 'Сначала выберите день.', noSlots: 'На этот день свободного времени не осталось. Выберите другой.',
    slots: 'вариантов', slot1: 'вариант',
    missing: 'Укажите имя и e-mail, выберите день и время и отметьте согласие.',
    email: 'Похоже, e-mail указан неверно. На него придёт подтверждение.',
    taken: 'Это время только что заняли. Выберите другое.',
    rate: 'Слишком много запросов. Попробуйте через час или позвоните по номеру +357 97 840941.',
    failed: 'Запись не прошла. Позвоните по номеру +357 97 840941 или напишите в WhatsApp.',
    sending: 'Отправляем…',
    okTitle: 'Запрос на встречу отправлен',
    okBody: 'Сейчас придёт e-mail (на английском) о том, что запрос получен, а после моего подтверждения — второе письмо со всеми деталями: где, как и добавление в календарь. При необходимости вы можете отменить встречу по ссылке в письме и выбрать другое время.',
    again: 'Новая запись',
    place: 'Укажите, где встречаемся (кафе и район или адрес).',
    partner: 'Отметьте, что согласны на передачу ваших данных партнёру по общему страхованию.',
  };
  var RU_LABEL = { review: 'Ежегодный пересмотр', life: 'Страхование жизни', health: 'Здоровье / медицина', savings: 'Накопления', pension: 'Пенсия',
    children: 'Дети и образование', property: 'Жильё и ипотека', business: 'Бизнес', claim: 'Страховой случай', other: 'Другое',
    car: 'Автомобиль', home: 'Жильё (здание и имущество)', travel: 'Путешествия', business_general: 'Бизнес: ответственность и имущество',
    office: 'В офисе', video: 'Видеосвязь', phone: 'По телефону', cafe: 'В кафе на ваш выбор', client_place: 'У вас (дома или в офисе компании)' };
  var RU_PLACE = { cafe: 'В каком кафе? (название и район)', client_place: 'Адрес встречи' };
  function plural(n) {
    if (!RU) return n === 1 ? txt.slot1 : txt.slots;
    var a = n % 10, b = n % 100;
    return a === 1 && b !== 11 ? 'вариант' : a >= 2 && a <= 4 && (b < 12 || b > 14) ? 'варианта' : 'вариантов';
  }
  function ruConfig(c) {
    // Russian labels over the booking system's English ones
    var map = function (list) { (list || []).forEach(function (it) { if (RU_LABEL[it.key]) it.label = RU_LABEL[it.key]; if (it.place && RU_PLACE[it.key]) it.place = RU_PLACE[it.key]; }); };
    map(c.topics); map(c.modes);
    if (c.general) {
      map(c.general.topics); map(c.general.modes);
      var p = c.general.partner || {}, who = (p.partner_name || '') + (p.partner_firm ? ' (' + p.partner_firm + ')' : '');
      c.general.group_life = 'Жизнь, здоровье, накопления, пенсия'; c.general.group_general = 'Общее страхование (с партнёром)';
      c.general.notice = 'По автомобилю, жилью, путешествиям и бизнесу консультацию и страховку предоставляет партнёр: ' + who + ', зарегистрированный страховой посредник по общему страхованию, рег. № ' + (p.partner_reg || '') + '. Яннис Фаразис зарегистрирован для страхования жизни и не консультирует по продуктам общего страхования.';
      c.general.consent = 'Я согласен(на) на передачу моего имени, контактных данных, темы и места встречи партнёру ' + who + ' для этой встречи.';
    }
    return c;
  }

  var $ = function (s) { return root.querySelector(s); };
  var form = $('form'), daysBox = $('[data-days]'), slotsBox = $('[data-slots]'), status = $('.status'), submit = $('button[type=submit]');
  var state = { date: '', time: '', token: '', tokenAt: 0, all: false };
  var more = $('[data-more]');
  more.addEventListener('click', function () { state.all = true; loadDays(); });

  function show(kind, text) { status.className = 'status ' + kind; status.textContent = text; if (kind === 'err') status.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
  function call(path, opts) {
    opts = opts || {};
    var headers = { 'X-Vero-Lang': LANG };
    if (opts.body) headers['Content-Type'] = 'application/json';
    return fetch(API + path, { method: opts.body ? 'POST' : 'GET', headers: headers, body: opts.body ? JSON.stringify(opts.body) : undefined, credentials: 'omit', cache: 'no-store', mode: 'cors' })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (b) { return { ok: r.ok, status: r.status, b: b }; }); });
  }
  function token() {
    return call('/form-token').then(function (r) { if (!r.ok || !r.b.token) throw new Error('token'); state.token = r.b.token; state.tokenAt = Date.now(); });
  }
  function dayLabel(iso) {
    var p = iso.split('-'), d = new Date(Date.UTC(+p[0], +p[1] - 1, +p[2], 12));
    return {
      wd: d.toLocaleDateString(LOCALE, { weekday: 'short', timeZone: TZ }),
      dm: d.toLocaleDateString(LOCALE, { day: 'numeric', month: 'short', timeZone: TZ }),
      long: d.toLocaleDateString(LOCALE, { weekday: 'long', day: 'numeric', month: 'long', timeZone: TZ }),
    };
  }
  function chip(label, sub, pressed, onClick) {
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'chip'; b.setAttribute('aria-pressed', pressed ? 'true' : 'false');
    var s = document.createElement('span'); s.textContent = label; b.appendChild(s);
    if (sub) { var m = document.createElement('small'); m.textContent = sub; b.appendChild(m); }
    b.addEventListener('click', onClick);
    return b;
  }
  function note(box, text) { box.textContent = ''; var p = document.createElement('p'); p.className = 'hint'; p.textContent = text; box.appendChild(p); }

  function loadDays() {
    note(daysBox, txt.loading); note(slotsBox, txt.pickDay);
    return call('/booking/days').then(function (r) {
      if (!r.ok) throw new Error('days');
      var days = r.b.days || [];
      daysBox.textContent = '';
      if (!days.length) { more.hidden = true; return note(daysBox, txt.none); }
      // the first two weeks first; the rest one tap away (keeps the phone page short)
      var limit = state.all ? days.length : 9, chosenAt = days.findIndex(function (d) { return d.date === state.date; });
      if (chosenAt >= limit) limit = days.length;
      more.hidden = limit >= days.length;
      days.slice(0, limit).forEach(function (d) {
        var l = dayLabel(d.date);
        var b = chip(l.wd + ' ' + l.dm, d.slots + ' ' + plural(d.slots), d.date === state.date, function () { pickDay(d.date); });
        b.setAttribute('aria-label', l.long + ', ' + d.slots + ' ' + plural(d.slots));
        b.setAttribute('data-date', d.date);
        daysBox.appendChild(b);
      });
      if (state.date && !days.some(function (d) { return d.date === state.date; })) { state.date = ''; state.time = ''; }
      if (state.date) return loadSlots();
    }).catch(function () { note(daysBox, txt.down); });
  }
  function pickDay(date) {
    state.date = date; state.time = '';
    [].forEach.call(daysBox.querySelectorAll('.chip'), function (c) { c.setAttribute('aria-pressed', c.getAttribute('data-date') === date ? 'true' : 'false'); });
    loadSlots();
  }
  function loadSlots() {
    note(slotsBox, txt.loading);
    return call('/booking/slots?date=' + encodeURIComponent(state.date)).then(function (r) {
      if (!r.ok) throw new Error('slots');
      var slots = r.b.slots || [];
      slotsBox.textContent = '';
      if (!slots.length) return note(slotsBox, txt.noSlots);
      slots.forEach(function (t) {
        var b = chip(t, '', t === state.time, function () {
          state.time = t;
          [].forEach.call(slotsBox.querySelectorAll('.chip'), function (c) { c.setAttribute('aria-pressed', c.textContent === t ? 'true' : 'false'); });
        });
        slotsBox.appendChild(b);
      });
    }).catch(function () { note(slotsBox, txt.down); });
  }

  function send(data, retried) {
    var wait = Math.max(0, 2500 - (Date.now() - state.tokenAt));
    return new Promise(function (ok) { setTimeout(ok, wait); }).then(function () {
      data.form_token = state.token;
      return call('/booking', { body: data });
    }).then(function (r) {
      if (r.ok && r.b.ok) return done(data);
      var code = r.b && r.b.code;
      if (!retried && (code === 'vero_form_expired' || code === 'vero_too_fast')) return token().then(function () { return send(data, true); });
      if (r.status === 429) return show('err', txt.rate);
      if (code === 'vero_slot_taken' || (r.b && r.b.data && r.b.data.fields && r.b.data.fields.time)) { state.time = ''; loadDays(); return show('err', txt.taken); }
      var f = r.b && r.b.data && r.b.data.fields;
      if (f) { var k = Object.keys(f); return show('err', k.map(function (x) { return f[x]; }).join(' ')); }
      show('err', (r.b && r.b.message) || txt.failed);
    });
  }
  function done(data) {
    var l = dayLabel(data.date);
    form.hidden = true;
    var box = $('[data-done]');
    box.querySelector('h2').textContent = txt.okTitle;
    box.querySelector('[data-when]').textContent = l.long + ' · ' + data.time;
    box.querySelector('[data-body]').textContent = txt.okBody;
    box.querySelector('[data-again]').textContent = txt.again;
    box.hidden = false; box.focus();
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var f = form.elements;
    var data = {
      name: f.name.value.trim(), email: f.email.value.trim(), phone: f.phone.value.trim(), topic: f.topic.value, mode: f.mode.value,
      note: f.note.value.trim(), date: state.date, time: state.time, privacy: f.privacy.checked, vc_hp_x: f.vc_hp_x.value,
    };
    // general insurance (with the partner): where we meet, and the agreement that the partner gets the details
    if (isGeneral()) {
      data.partner_consent = f.partner_consent.checked;
      if (needsPlace()) data.place = f.place.value.trim();
      if (needsPlace() && data.place.length < 3) return show('err', txt.place);
      if (!data.partner_consent) return show('err', txt.partner);
    }
    if (data.name.length < 2 || !data.email || !data.date || !data.time || !data.privacy) return show('err', txt.missing);
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(data.email)) return show('err', txt.email);
    var label = submit.textContent; submit.disabled = true; submit.textContent = txt.sending; status.className = 'status';
    (state.token ? Promise.resolve() : token()).then(function () { return send(data, false); })
      .catch(function () { show('err', txt.failed); })
      .then(function () { submit.disabled = false; submit.textContent = label; });
  });
  $('[data-again]').addEventListener('click', function () {
    form.reset(); topicChanged(); state.date = ''; state.time = ''; state.all = false; $('[data-done]').hidden = true; form.hidden = false; token().catch(function () {}); loadDays();
  });

  // 1.6: general topics meet only at a café the visitor names or at their own place, never at the office
  var cfg = { life: [], general: null };
  function isGeneral() { return !!cfg.general && cfg.general.topics.some(function (t) { return t.key === form.elements.topic.value; }); }
  function modeInfo() { var m = form.elements.mode.value; return (isGeneral() ? cfg.general.modes : cfg.life).filter(function (x) { return x.key === m; })[0] || {}; }
  function needsPlace() { return !!modeInfo().place; }
  function syncPlace() {
    var box = $('[data-place]'), need = isGeneral() && needsPlace();
    box.hidden = !need; form.elements.place.disabled = !need;
    if (need) $('[data-place-label]').textContent = modeInfo().place;
  }
  function topicChanged() {
    var gen = isGeneral(), sel = form.elements.mode, keep = sel.value, list = gen ? cfg.general.modes : cfg.life;
    if (list && list.length) {
      sel.textContent = '';
      list.forEach(function (it) { var o = document.createElement('option'); o.value = it.key; o.textContent = it.label; sel.appendChild(o); });
      if (list.some(function (x) { return x.key === keep; })) sel.value = keep;
    }
    $('[data-general]').hidden = !gen; form.elements.partner_consent.disabled = !gen;
    syncPlace();
  }
  form.elements.topic.addEventListener('change', topicChanged);
  form.elements.mode.addEventListener('change', syncPlace);

  // what the advisor offers (topics, ways to meet, links to the booking system's privacy notice and terms)
  call('/booking/config').then(function (r) {
    if (!r.ok) throw new Error('config');
    var c = RU ? ruConfig(r.b) : r.b;
    if (!c.available) { form.hidden = true; return show('err', txt.off); }
    var fill = function (sel, items) { if (!items || !items.length) return; sel.textContent = ''; items.forEach(function (it) { var o = document.createElement('option'); o.value = it.key; o.textContent = it.label; sel.appendChild(o); }); };
    var want = root.getAttribute('data-topic');
    fill(form.elements.topic, c.topics); fill(form.elements.mode, c.modes);
    cfg.life = c.modes || []; cfg.general = c.general || null;
    if (cfg.general) {
      // two groups: life cover with me, general insurance with my licensed partner
      var sel = form.elements.topic, g1 = document.createElement('optgroup'), g2 = document.createElement('optgroup');
      g1.label = cfg.general.group_life; g2.label = cfg.general.group_general;
      [].slice.call(sel.options).forEach(function (o) { g1.appendChild(o); });
      cfg.general.topics.forEach(function (it) { var o = document.createElement('option'); o.value = it.key; o.textContent = it.label; g2.appendChild(o); });
      sel.appendChild(g1); sel.appendChild(g2);
      sel.selectedIndex = 0;   // moving the options into groups can leave the last one selected
      $('[data-general-notice]').textContent = cfg.general.notice;
      $('[data-partner-consent]').textContent = cfg.general.consent;
    }
    if (want && [].some.call(form.elements.topic.options, function (o) { return o.value === want; })) form.elements.topic.value = want;
    topicChanged();
    if (c.privacy_url) $('[data-privacy]').href = c.privacy_url;
    if (c.terms_url) $('[data-terms]').href = c.terms_url;
    if (c.minutes) $('[data-minutes]').textContent = String(c.minutes);
    root.classList.add('is-ready');
  }).catch(function () { root.classList.add('is-ready'); });
  var q = new URLSearchParams(location.search).get('topic');
  if (q) root.setAttribute('data-topic', q);
  token().catch(function () {});
  loadDays();
  document.addEventListener('visibilitychange', function () { if (!document.hidden && !form.hidden) loadDays(); });
})();
